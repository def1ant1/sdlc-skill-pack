terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  backend "s3" {
    # Configure via -backend-config or environment variables
    # bucket = "your-terraform-state-bucket"
    # key    = "apotheon/terraform.tfstate"
    # region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# ── EKS Cluster ──────────────────────────────────────────────────────────────

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      instance_types = [var.node_instance_type]
      min_size       = 2
      max_size       = 10
      desired_size   = var.node_desired_count

      labels = {
        workload = "apotheon"
      }
    }
  }

  tags = local.common_tags
}

# ── VPC ──────────────────────────────────────────────────────────────────────

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_dns_hostnames = true

  tags = local.common_tags
}

# ── RDS PostgreSQL ────────────────────────────────────────────────────────────

resource "aws_db_instance" "apotheon" {
  identifier             = "${var.cluster_name}-postgres"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  max_allocated_storage  = 100
  storage_encrypted      = true

  db_name  = "apotheon"
  username = "apotheon"
  password = var.db_password  # Use AWS Secrets Manager in production

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.apotheon.name

  backup_retention_period = 7
  deletion_protection     = var.environment == "production"
  skip_final_snapshot     = var.environment != "production"

  tags = local.common_tags
}

resource "aws_db_subnet_group" "apotheon" {
  name       = "${var.cluster_name}-db-subnet"
  subnet_ids = module.vpc.private_subnets
  tags       = local.common_tags
}

resource "aws_security_group" "rds" {
  name   = "${var.cluster_name}-rds-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  tags = local.common_tags
}

# ── ElastiCache Redis ─────────────────────────────────────────────────────────

resource "aws_elasticache_cluster" "apotheon" {
  cluster_id           = "${var.cluster_name}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.apotheon.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = local.common_tags
}

resource "aws_elasticache_subnet_group" "apotheon" {
  name       = "${var.cluster_name}-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name   = "${var.cluster_name}-redis-sg"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  tags = local.common_tags
}

# ── Helm Release ──────────────────────────────────────────────────────────────

resource "helm_release" "apotheon" {
  name       = "apotheon"
  chart      = "${path.module}/../helm/apotheon"
  namespace  = "apotheon"
  create_namespace = true

  set {
    name  = "image.tag"
    value = var.image_tag
  }

  set_sensitive {
    name  = "env.ANTHROPIC_API_KEY"
    value = var.anthropic_api_key
  }

  set_sensitive {
    name  = "env.DATABASE_URL"
    value = "postgresql+asyncpg://apotheon:${var.db_password}@${aws_db_instance.apotheon.endpoint}/apotheon"
  }

  set_sensitive {
    name  = "env.REDIS_URL"
    value = "redis://${aws_elasticache_cluster.apotheon.cache_nodes[0].address}:6379"
  }

  set_sensitive {
    name  = "env.JWT_SECRET"
    value = var.jwt_secret
  }

  depends_on = [module.eks, aws_db_instance.apotheon, aws_elasticache_cluster.apotheon]
}

# ── Locals ────────────────────────────────────────────────────────────────────

locals {
  common_tags = {
    Project     = "apotheon"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}