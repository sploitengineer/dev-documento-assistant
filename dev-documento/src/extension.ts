import * as vscode from 'vscode';
import axios from 'axios';

// The base URL for your local Flask server
const API_BASE_URL = 'http://127.0.0.1:5000';

// This method is called when your extension is activated
export function activate(context: vscode.ExtensionContext) {

    // --- COMMAND: Generate Documentation ---
    let generateDocsCommand = vscode.commands.registerCommand('dev-documento.generateDocs', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor found.');
            return;
        }

        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);

        if (!selectedText) {
            vscode.window.showInformationMessage('No text selected.');
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Dev-Doc: Generating documentation...",
            cancellable: false
        }, async (progress) => {
            try {
                const response = await axios.post(`${API_BASE_URL}/document`, { code: selectedText });
                let documentation = response.data.documentation;

                // --- NEW: INDENTATION LOGIC ---
                // Get the line where the selection starts to determine the indentation level
                const startLine = editor.document.lineAt(selection.start.line);
                const baseIndentation = startLine.text.substring(0, startLine.firstNonWhitespaceCharacterIndex);

                // Indent every line of the generated documentation to match the function's indentation
                const indentedDocumentation = documentation.split('\n').map((line: string) => `${baseIndentation}${line}`).join('\n');

                // Insert the formatted documentation above the selected code
                editor.edit(editBuilder => {
                    editBuilder.insert(selection.start, indentedDocumentation + '\n');
                });

            } catch (error) {
                console.error(error);
                vscode.window.showErrorMessage('Failed to generate documentation. Is the backend server running?');
            }
        });
    });

    // --- COMMAND: Run Code Review ---
    let runReviewCommand = vscode.commands.registerCommand('dev-documento.runReview', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }
        const selectedText = editor.document.getText(editor.selection);
        if (!selectedText) {
            vscode.window.showInformationMessage('No text selected for review.');
            return;
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Dev-Doc: Running code review...",
            cancellable: false
        }, async (progress) => {
            try {
                const response = await axios.post(`${API_BASE_URL}/review`, { code: selectedText });
                const review = response.data.review;

                // --- NEW: DISPLAY REVIEW IN A NEW MARKDOWN TAB ---
                const reviewDoc = await vscode.workspace.openTextDocument({
                    content: `# Dev-Doc Code Review\n\n${review}`,
                    language: 'markdown'
                });

                await vscode.window.showTextDocument(reviewDoc, vscode.ViewColumn.Beside, true);

            } catch (error) {
                console.error(error);
                vscode.window.showErrorMessage('Failed to get code review. Is the backend server running?');
            }
        });
    });

    context.subscriptions.push(generateDocsCommand, runReviewCommand);
}

export function deactivate() {}
