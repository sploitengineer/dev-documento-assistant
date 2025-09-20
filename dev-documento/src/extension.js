"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
// The base URL for your local Flask server
const API_BASE_URL = 'http://127.0.0.1:5000';
// This method is called when your extension is activated
function activate(context) {
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
        // Show a progress indicator
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Dev-Doc: Generating documentation...",
            cancellable: false
        }, async (progress) => {
            try {
                // Make API call to the backend
                const response = await axios_1.default.post(`${API_BASE_URL}/document`, { code: selectedText });
                const documentation = response.data.documentation;
                // Insert the generated documentation above the selected code
                editor.edit(editBuilder => {
                    editBuilder.insert(selection.start, documentation + '\n');
                });
            }
            catch (error) {
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
                // Make API call to the backend
                const response = await axios_1.default.post(`${API_BASE_URL}/review`, { code: selectedText });
                const review = response.data.review;
                // Show the review feedback in an information message
                vscode.window.showInformationMessage(`Dev-Doc Review: ${review}`);
            }
            catch (error) {
                console.error(error);
                vscode.window.showErrorMessage('Failed to get code review. Is the backend server running?');
            }
        });
    });
    context.subscriptions.push(generateDocsCommand, runReviewCommand);
}
// This method is called when your extension is deactivated
function deactivate() { }
//# sourceMappingURL=extension.js.map