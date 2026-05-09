import * as vscode from 'vscode';

// ── API client ────────────────────────────────────────────────────────────────

function getConfig() {
    const cfg = vscode.workspace.getConfiguration('apotheon');
    return {
        apiUrl: cfg.get<string>('apiUrl', 'http://localhost:8000'),
        apiToken: cfg.get<string>('apiToken', ''),
        defaultModel: cfg.get<string>('defaultModel', 'claude-sonnet-4-6'),
    };
}

async function apiFetch(path: string, options: RequestInit = {}): Promise<unknown> {
    const { apiUrl, apiToken } = getConfig();
    const url = `${apiUrl}${path}`;
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> || {}),
    };
    if (apiToken) {
        headers['Authorization'] = `Bearer ${apiToken}`;
    }
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
        const body = await res.text();
        throw new Error(`API ${res.status}: ${body}`);
    }
    return res.json();
}

// ── Commands ──────────────────────────────────────────────────────────────────

async function cmdRunSkill(): Promise<void> {
    const skills = [
        'requirements', 'architecture', 'ai-engineering', 'backend',
        'frontend', 'code-review', 'qa', 'devsecops', 'release-management',
        'observability', 'sre', 'compliance-automation', 'executive-reporting',
    ];

    const skill = await vscode.window.showQuickPick(skills, {
        placeHolder: 'Select a skill to run',
        title: 'Apotheon: Run Skill',
    });
    if (!skill) { return; }

    const objective = await vscode.window.showInputBox({
        prompt: 'Enter objective for this skill',
        placeHolder: 'e.g. Review the auth module for security issues',
    });
    if (!objective) { return; }

    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: `Running ${skill}...`, cancellable: false },
        async () => {
            try {
                const result = await apiFetch('/v1/workflows', {
                    method: 'POST',
                    body: JSON.stringify({
                        objective,
                        plan: { skill_chain: [{ skill }] },
                        mode: 'local',
                    }),
                }) as { run_id: string };
                vscode.window.showInformationMessage(
                    `Workflow started: ${result.run_id}`,
                    'View Status'
                ).then(action => {
                    if (action === 'View Status') {
                        vscode.commands.executeCommand('apotheon.openDashboard');
                    }
                });
            } catch (err) {
                vscode.window.showErrorMessage(`Failed to start workflow: ${err}`);
            }
        }
    );
}

async function cmdPlanWorkflow(): Promise<void> {
    const objective = await vscode.window.showInputBox({
        prompt: 'Describe your SDLC objective',
        placeHolder: 'e.g. Build a REST API with auth and deploy to AWS',
    });
    if (!objective) { return; }

    await vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title: 'Planning workflow...', cancellable: false },
        async () => {
            try {
                const estimate = await apiFetch('/v1/cost/estimate', {
                    method: 'POST',
                    body: JSON.stringify({
                        plan: {
                            skill_chain: [
                                { skill: 'requirements' },
                                { skill: 'architecture' },
                                { skill: 'backend' },
                                { skill: 'code-review' },
                                { skill: 'qa' },
                            ],
                        },
                    }),
                }) as { total_cost_usd: number; total_input_tokens: number; total_output_tokens: number };

                const proceed = await vscode.window.showInformationMessage(
                    `Estimated cost: $${estimate.total_cost_usd.toFixed(4)} ` +
                    `(${estimate.total_input_tokens + estimate.total_output_tokens} tokens)`,
                    'Run Workflow', 'Cancel'
                );

                if (proceed === 'Run Workflow') {
                    await cmdRunSkill();
                }
            } catch (err) {
                vscode.window.showErrorMessage(`Planning failed: ${err}`);
            }
        }
    );
}

async function cmdApproveHITL(item?: HITLTreeItem): Promise<void> {
    const id = item?.approvalId || await vscode.window.showInputBox({ prompt: 'Approval ID' });
    if (!id) { return; }

    try {
        await apiFetch(`/v1/approvals/${id}/decide`, {
            method: 'POST',
            body: JSON.stringify({ decision: 'approved', comment: 'Approved via VS Code' }),
        });
        vscode.window.showInformationMessage('HITL gate approved.');
        vscode.commands.executeCommand('apotheon.refreshRuns');
    } catch (err) {
        vscode.window.showErrorMessage(`Approval failed: ${err}`);
    }
}

async function cmdRejectHITL(item?: HITLTreeItem): Promise<void> {
    const id = item?.approvalId || await vscode.window.showInputBox({ prompt: 'Approval ID' });
    if (!id) { return; }

    const reason = await vscode.window.showInputBox({ prompt: 'Rejection reason (optional)' });

    try {
        await apiFetch(`/v1/approvals/${id}/decide`, {
            method: 'POST',
            body: JSON.stringify({ decision: 'rejected', comment: reason || 'Rejected via VS Code' }),
        });
        vscode.window.showInformationMessage('HITL gate rejected.');
        vscode.commands.executeCommand('apotheon.refreshRuns');
    } catch (err) {
        vscode.window.showErrorMessage(`Rejection failed: ${err}`);
    }
}

// ── Tree Views ────────────────────────────────────────────────────────────────

class HITLTreeItem extends vscode.TreeItem {
    constructor(
        public readonly approvalId: string,
        label: string,
        description: string,
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.contextValue = 'hitlPending';
        this.iconPath = new vscode.ThemeIcon('warning', new vscode.ThemeColor('charts.yellow'));
    }
}

class HITLQueueProvider implements vscode.TreeDataProvider<HITLTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HITLTreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: HITLTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(): Promise<HITLTreeItem[]> {
        try {
            const result = await apiFetch('/v1/approvals') as Array<{
                id: string; skill_name: string; risk_level: string;
            }>;
            return result.map(a => new HITLTreeItem(
                a.id,
                a.skill_name,
                `Risk: ${a.risk_level}`,
            ));
        } catch {
            return [];
        }
    }
}

// ── Extension entry ───────────────────────────────────────────────────────────

export function activate(context: vscode.ExtensionContext): void {
    const hitlProvider = new HITLQueueProvider();

    vscode.window.registerTreeDataProvider('apotheon.hitlQueue', hitlProvider);

    context.subscriptions.push(
        vscode.commands.registerCommand('apotheon.runSkill', cmdRunSkill),
        vscode.commands.registerCommand('apotheon.planWorkflow', cmdPlanWorkflow),
        vscode.commands.registerCommand('apotheon.openDashboard', () => {
            const { apiUrl } = getConfig();
            vscode.env.openExternal(vscode.Uri.parse(`${apiUrl}/docs`));
        }),
        vscode.commands.registerCommand('apotheon.approveHITL', cmdApproveHITL),
        vscode.commands.registerCommand('apotheon.rejectHITL', cmdRejectHITL),
        vscode.commands.registerCommand('apotheon.refreshRuns', () => hitlProvider.refresh()),
    );

    // Auto-refresh
    const cfg = vscode.workspace.getConfiguration('apotheon');
    const interval = cfg.get<number>('autoRefreshInterval', 5);
    if (interval > 0) {
        const timer = setInterval(() => hitlProvider.refresh(), interval * 1000);
        context.subscriptions.push({ dispose: () => clearInterval(timer) });
    }

    vscode.window.showInformationMessage('Apotheon SDLC Skills extension activated.');
}

export function deactivate(): void {}