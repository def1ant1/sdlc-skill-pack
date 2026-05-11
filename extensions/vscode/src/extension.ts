import * as vscode from 'vscode';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import * as path from 'node:path';

const execFileAsync = promisify(execFile);

function getConfig() {
    const cfg = vscode.workspace.getConfiguration('apotheon');
    return {
        apiUrl: cfg.get<string>('apiUrl', 'http://localhost:8000'),
        apiToken: cfg.get<string>('apiToken', ''),
        defaultModel: cfg.get<string>('defaultModel', 'claude-sonnet-4-6'),
        pythonCommand: cfg.get<string>('pythonCommand', 'python3'),
    };
}

async function runRepoCommand(args: string[], title: string): Promise<{ stdout: string; stderr: string; }> {
    const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!folder) { throw new Error('Open this repository in VS Code first.'); }
    const { pythonCommand } = getConfig();
    return vscode.window.withProgress(
        { location: vscode.ProgressLocation.Notification, title, cancellable: false },
        async () => execFileAsync(pythonCommand, args, { cwd: folder, maxBuffer: 1024 * 1024 * 10 }),
    );
}

function repoPath(...parts: string[]): string {
    const folder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    return path.join(folder || '', ...parts);
}

async function cmdValidateManifests(): Promise<void> {
    try {
        const out = await runRepoCommand(['scripts/validation/validate_skill_yaml.py', '--mvp'], 'Validating skill manifests...');
        vscode.window.showInformationMessage('Manifest validation completed. See output channel for details.');
        const chan = vscode.window.createOutputChannel('Apotheon Validation');
        chan.appendLine(out.stdout || '(no stdout)');
        if (out.stderr) { chan.appendLine(out.stderr); }
        chan.show(true);
    } catch (err) { vscode.window.showErrorMessage(`Manifest validation failed: ${err}`); }
}

async function cmdDryRunLaunch(): Promise<void> {
    try {
        const planFile = repoPath('workflows/examples/business/company-operating-system-dry-run.workflow.json');
        const out = await runRepoCommand(['scripts/orchestration/execute_graph.py', '--plan', planFile, '--dry-run'], 'Running workflow dry-run...');
        const chan = vscode.window.createOutputChannel('Apotheon Dry Run');
        chan.appendLine(out.stdout || '(no stdout)');
        if (out.stderr) { chan.appendLine(out.stderr); }
        chan.show(true);
        vscode.window.showInformationMessage('Dry-run launch completed.');
    } catch (err) { vscode.window.showErrorMessage(`Dry-run failed: ${err}`); }
}

async function cmdOpenDiagnostics(): Promise<void> {
    try {
        await runRepoCommand(['scripts/reports/generate_runtime_diagnostics.py'], 'Generating diagnostics...');
        const diagUri = vscode.Uri.file(repoPath('runtime/diagnostics/runtime_diagnostics.json'));
        await vscode.commands.executeCommand('vscode.open', diagUri);
    } catch (err) { vscode.window.showErrorMessage(`Diagnostics failed: ${err}`); }
}

async function cmdOpenMaturityPanel(): Promise<void> {
    try {
        const out = await runRepoCommand(['scripts/grade_skill_maturity.py', '--profile', 'mvp'], 'Grading skill maturity...');
        const chan = vscode.window.createOutputChannel('Apotheon Maturity');
        chan.appendLine(out.stdout || '(no stdout)');
        if (out.stderr) { chan.appendLine(out.stderr); }
        chan.show(true);
    } catch (err) { vscode.window.showErrorMessage(`Maturity panel command failed: ${err}`); }
}

async function cmdImportTemplate(): Promise<void> {
    try {
        const out = await runRepoCommand(['scripts/company_templates/import_template.py', '--template', 'oldfarmtrucks'], 'Importing company template...');
        const chan = vscode.window.createOutputChannel('Apotheon Template Import');
        chan.appendLine(out.stdout || '(no stdout)');
        if (out.stderr) { chan.appendLine(out.stderr); }
        chan.show(true);
        vscode.window.showInformationMessage('Template import command completed.');
    } catch (err) { vscode.window.showErrorMessage(`Template import failed: ${err}`); }
}

class HITLTreeItem extends vscode.TreeItem {
    constructor(public readonly approvalId: string, label: string, description: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.description = description;
        this.contextValue = 'hitlPending';
    }
}
class HITLQueueProvider implements vscode.TreeDataProvider<HITLTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HITLTreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    refresh(): void { this._onDidChangeTreeData.fire(undefined); }
    getTreeItem(element: HITLTreeItem): vscode.TreeItem { return element; }
    async getChildren(): Promise<HITLTreeItem[]> { return []; }
}

export function activate(context: vscode.ExtensionContext): void {
    const hitlProvider = new HITLQueueProvider();
    vscode.window.registerTreeDataProvider('apotheon.hitlQueue', hitlProvider);
    context.subscriptions.push(
        vscode.commands.registerCommand('apotheon.validateManifests', cmdValidateManifests),
        vscode.commands.registerCommand('apotheon.dryRunLaunch', cmdDryRunLaunch),
        vscode.commands.registerCommand('apotheon.openDiagnostics', cmdOpenDiagnostics),
        vscode.commands.registerCommand('apotheon.openMaturityPanel', cmdOpenMaturityPanel),
        vscode.commands.registerCommand('apotheon.importTemplate', cmdImportTemplate),
    );
}

export function deactivate(): void {}
