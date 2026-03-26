'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, ChevronDown, Settings, AlertCircle } from 'lucide-react';
import { FindingsPanel } from './FindingsPanel';
import { WorkflowStatus } from './WorkflowStatus';

// Match the Action type that WorkflowStatus expects
type ActionStatus = 'pending' | 'running' | 'completed' | 'failed';

interface WorkflowAction {
  tool: string;
  action: string;
  status: ActionStatus;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  severity?: string;
  findings?: Record<string, any>;
  remediation_plan?: string;
  executed_actions?: WorkflowAction[];
}

// Raw action shape from API (status can be any string)
interface APIAction {
  tool: string;
  action: string;
  status: string;
}

interface APIResponse {
  status: string;
  severity?: string;
  workflow_type?: string;
  findings: Record<string, any>;
  remediation_plan?: string;
  executed_actions: APIAction[];
  error?: string;
}

const EXAMPLE_QUERIES = [
  'Show me high CPU pods in production',
  'Get logs from failing pods',
  'Restart unhealthy pods',
  'Analyze cluster costs and find waste',
  'Get software inventory from all hosts',
  'List all Helm releases',
  'Get all pods in default namespace',
];

// Map any string status from the API into our strict union
const normalizeStatus = (status: string): ActionStatus => {
  switch (status.toLowerCase()) {
    case 'completed':
    case 'success':
    case 'done':
      return 'completed';
    case 'failed':
    case 'error':
    case 'errored':
      return 'failed';
    case 'running':
    case 'in_progress':
    case 'in-progress':
      return 'running';
    case 'pending':
    default:
      return 'pending';
  }
};

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content:
        'Welcome to NimbusRE Agent! I can help you monitor, troubleshoot, and optimize your Kubernetes clusters. Ask me about metrics, logs, remediation, or cost analysis.',
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [apiHealth, setApiHealth] = useState<'healthy' | 'unhealthy' | 'checking'>('checking');
  const [selectedWorkflowType, setSelectedWorkflowType] = useState<'basic' | 'advanced'>('basic');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/sre');
        if (response.ok) {
          setApiHealth('healthy');
        } else {
          setApiHealth('unhealthy');
        }
      } catch (err) {
        setApiHealth('unhealthy');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    if (apiHealth === 'unhealthy') {
      setError('API backend is not available. Please check if the Python server is running.');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/sre', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage.content,
          workflow_type: selectedWorkflowType,
          max_tools: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: APIResponse = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      const executedActions: WorkflowAction[] =
        data.executed_actions?.map((a) => ({
          tool: a.tool,
          action: a.action,
          status: normalizeStatus(a.status),
        })) ?? [];

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.remediation_plan || 'Analysis complete. See findings in the sidebar.',
        timestamp: new Date(),
        severity: data.severity,
        findings: data.findings,
        remediation_plan: data.remediation_plan,
        executed_actions: executedActions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);

      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        id: '0',
        role: 'assistant',
        content:
          'Welcome to NimbusREAgent! I can help you monitor, troubleshoot, and optimize your Kubernetes clusters.',
        timestamp: new Date(),
      },
    ]);
    setError(null);
  };

  const handleExampleClick = (query: string) => {
    setInput(query);
  };

  const currentMessage = messages[messages.length - 1];

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/nimbus.png"
              alt="Nimbus Logo"
              style={{ width: 24, height: 24 }}
              className="max-w-[24px] max-h-[24px] rounded-lg object-contain flex-shrink-0 inline-block align-middle"
            />
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">NimbusRE Agent</h1>
              <p className="text-base font-bold text-yellow-300 drop-shadow-lg">Cloud Reliability Engineering Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* API Health */}
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800">
              <div
                className={`w-2 h-2 rounded-full ${
                  apiHealth === 'healthy'
                    ? 'bg-green-500'
                    : apiHealth === 'unhealthy'
                    ? 'bg-red-500'
                    : 'bg-yellow-500'
                }`}
              />
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {apiHealth === 'healthy'
                  ? 'Connected'
                  : apiHealth === 'unhealthy'
                  ? 'Disconnected'
                  : 'Checking'}
              </span>
            </div>

            {/* Workflow Type Toggle */}
            <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                onClick={() => setSelectedWorkflowType('basic')}
                className={`px-3 py-1 rounded text-xs font-medium transition ${
                  selectedWorkflowType === 'basic'
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Basic
              </button>
              <button
                onClick={() => setSelectedWorkflowType('advanced')}
                className={`px-3 py-1 rounded text-xs font-medium transition ${
                  selectedWorkflowType === 'advanced'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Advanced
              </button>
            </div>

            {/* Clear Button */}
            <button
              onClick={handleClear}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
              title="Clear chat"
            >
              <Trash2 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>

            {/* Toggle Sidebar */}
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
            >
              <ChevronDown
                className={`w-5 h-5 text-gray-600 dark:text-gray-400 transition-transform ${
                  showSidebar ? 'rotate-180' : ''
                }`}
              />
            </button>
          </div>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 1 && (
            <div className="h-full flex items-center justify-center">
              <div className="max-w-md">
                <div className="bg-white dark:bg-gray-900 rounded-lg p-8 border border-gray-200 dark:border-gray-800">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                    Quick Start Examples
                  </h2>
                  <div className="space-y-2">
                    {EXAMPLE_QUERIES.map((query, idx) => {
                      const icons = ['📊', '📋', '🔧', '💰', '🔍', '⚓', '☸️'];
                      const labels = ['Monitor', 'Logs', 'Healing', 'Cost', 'Ansible', 'Helm', 'Kubectl'];
                      return (
                        <button
                          key={idx}
                          onClick={() => handleExampleClick(query)}
                          className="w-full text-left p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition text-sm text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700"
                        >
                          {icons[idx]} <strong>{labels[idx]}:</strong> {query}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className="flex gap-4 animate-fade-in">
              {/* Avatar */}
              <div className="flex-shrink-0">
                {msg.role === 'user' ? (
                  <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white text-sm font-bold">
                    U
                  </div>
                ) : (
                  <img
                    src="/nimbus.png"
                    alt="Assistant"
                    style={{ width: 24, height: 24 }}
                    className="max-w-[24px] max-h-[24px] rounded-lg object-contain"
                  />
                )}
              </div>

              {/* Message Content */}
              <div className="flex-1">
                <div
                  className={`p-4 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-gray-900 dark:text-white'
                      : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-900 dark:text-white'
                  }`}
                >
                  <p className="whitespace-pre-wrap text-base leading-relaxed">{msg.content}</p>
                </div>

                {/* Message Metadata */}
                {msg.role === 'assistant' && (msg.severity || msg.executed_actions?.length) && (
                  <div className="mt-3 space-y-2 text-xs text-gray-600 dark:text-gray-400">
                    {msg.severity && (
                      <span className="inline-block px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
                        🎯 Severity: <strong>{msg.severity}</strong>
                      </span>
                    )}
                    {msg.executed_actions && msg.executed_actions.length > 0 && (
                      <span className="inline-block ml-2 px-2 py-1 rounded bg-gray-100 dark:bg-gray-800">
                        ✓ Actions: <strong>{msg.executed_actions.length}</strong>
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center text-white text-sm font-bold">
                AI
              </div>
              <div className="flex-1">
                <div className="p-4 rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex gap-3">
              <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
              <div className="flex-1 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about monitoring, logs, healing, or costs..."
                className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 resize-none overflow-y-auto"
                rows={8}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium transition flex items-center gap-2 h-fit"
              >
                <Send className="w-4 h-4" />
                {loading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Right Sidebar */}
      {showSidebar && currentMessage?.role === 'assistant' && (
        <div className="w-80 border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Workflow Status */}
            <div>
              <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Status
              </h3>
              <WorkflowStatus
                workflow_type={currentMessage?.remediation_plan ? 'advanced' : 'basic'}
                severity={currentMessage?.severity}
                executed_actions={currentMessage?.executed_actions}
                is_loading={loading}
              />
            </div>

            {/* Findings Panel */}
            {(currentMessage?.findings || currentMessage?.remediation_plan) && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-4">
                  Findings & Actions
                </h3>
                <FindingsPanel
                  findings={currentMessage?.findings || {}}
                  severity={currentMessage?.severity}
                  remediation_plan={currentMessage?.remediation_plan}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
