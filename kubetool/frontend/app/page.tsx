"use client"

import { useState, useRef, useEffect } from "react"
import axios from "axios"
import { useChatStore } from "@/lib/store"
import type { Message, SREQueryResult } from "@/lib/types"
import {
  Send,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function ChatInterface() {
  const {
    messages,
    workflowState,
    isLoading,
    addMessage,
    updateWorkflowState,
    setLoading,
    clearChat,
    getRecentQueries,
  } = useChatStore()

  const [input, setInput] = useState("")
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const recentQueries = getRecentQueries()

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    addMessage(userMessage)
    setInput("")
    setLoading(true)
    setError(null)

    try {
      // Call API via Next.js route
      const response = await axios.post<SREQueryResult>(
        `/api/sre`,
        { query: input },
        { timeout: 300000 }
      )

      const result = response.data

      // Update workflow state
      if (result.error) {
        setError(result.error)
        return
      }

      if (result.state) {
        const safeState = {
          ...result.state,
          status: mapStatus(result.state.status) ?? "idle",
        }
        updateWorkflowState(safeState)
      }

      // Add bot message
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content:
          result.remediation_plan ||
          "Analysis complete. Check the findings panel for details.",
        timestamp: new Date(),
        findings: result.findings,
        metadata: {
          severity: result.state?.severity,
          status: result.state?.status,
        },
      }

      addMessage(botMessage)
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.error ||
        err.message ||
        "An error occurred while processing your request"
      setError(errorMsg)

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "bot",
        content: `❌ Error: ${errorMsg}`,
        timestamp: new Date(),
      }

      addMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleQuickQuery = (query: string) => {
    setInput(query)
  }

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-900/30 text-red-400"
      case "high":
        return "bg-orange-900/30 text-orange-400"
      case "medium":
        return "bg-yellow-900/30 text-yellow-400"
      case "low":
        return "bg-green-900/30 text-green-400"
      default:
        return "bg-blue-900/30 text-blue-400"
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case "executing":
        return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="border-b border-blue-300 bg-blue-600 backdrop-blur" style={{ backgroundColor: '#3b82f6', borderBottomColor: '#93c5fd', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">  
            <div>
              <Zap className="w-8 h-8 text-white/70 mb-2" />
               <h1 className="text-2xl font-bold text-white drop-shadow-lg">
             NimbusRE Agent</h1>
              <p className="text-xl font-black text-red-500" style={{textShadow: '2px 2px 4px rgba(0,0,0,0.8)'}}>
                Cloud Reliability Engineering Assistant
              </p>
          </div>
          {messages.length > 0 && (
            <Button
              onClick={clearChat}
              variant="secondary"
              size="sm"
            >
              Clear Chat
            </Button>
          )}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <Zap className="w-16 h-16 text-sre-secondary/50 mb-4" />
                <h2 className="text-2xl font-bold text-white mb-2">

                  Welcome to NimbusRE Agent
                </h2>
                <p className="text-gray-400 mb-8 max-w-md">
                  Ensure system reliability, automate incident response, and maintain optimal cloud infrastructure performance with intelligent SRE automation.
                </p>

                {/* Quick Actions */}
                <div className="grid grid-cols-3 gap-3 w-full max-w-4xl">
                  <Button
                    onClick={() =>
                      handleQuickQuery("Show me high CPU pods in production")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">📊 Monitor</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Check cluster metrics
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("Get logs from failing pods")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">📋 Logs</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Aggregate pod logs
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("Restart unhealthy pods")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">🔧 Healing</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Self-healing actions
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("Analyze cluster costs and find waste")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">💰 Cost</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Cost analysis & optimization
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("Get software inventory from all hosts")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">🔍 Ansible</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Host inventory & status
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("List all Helm releases")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">⚓ Helm</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Deploy & manage charts
                    </div>
                  </Button>
                  <Button
                    onClick={() =>
                      handleQuickQuery("Get all pods in default namespace")
                    }
                    variant="outline"
                    className="h-auto p-4 flex flex-col items-start text-left"
                  >
                    <div className="font-semibold text-sm">☸️ Kubectl</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Kubernetes resources
                    </div>
                  </Button>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-4xl p-6 rounded-lg shadow-lg ${
                        message.role === "user"
                          ? "bg-blue-600 text-white rounded-tr-none"
                          : "bg-white text-gray-800 rounded-tl-none border border-gray-200"
                      }`}
                      style={{ minHeight: '80px', width: '90%' }}
                    >
                      {message.metadata?.severity && (
                        <div className="mb-2">
                          <span
                            className={`badge ${getSeverityColor(
                              message.metadata.severity
                            )}`}
                          >
                            {message.metadata.severity.toUpperCase()}
                          </span>
                        </div>
                      )}
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </p>
                      {message.findings && Object.keys(message.findings).length > 0 && (
                        <Card className="mt-4">
                          <CardHeader>
                            <CardTitle className="text-sm">🔍 Findings</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <Table>
                              <TableHeader>
                                <TableRow style={{ background: 'linear-gradient(to right, #1e40af, #1d4ed8)' }}>
                                  <TableHead className="w-1/4" style={{ color: '#ffffff' }}>Tool</TableHead>
                                  <TableHead className="w-1/2" style={{ color: '#ffffff' }}>Result</TableHead>
                                  <TableHead className="w-1/4" style={{ color: '#ffffff' }}>Status</TableHead>
                                </TableRow>
                              </TableHeader>
                              <TableBody>
                                {Object.entries(message.findings).map(([key, value], index) => {
                                  const isError = typeof value === 'object' && value?.error;
                                  const rowStyle = isError 
                                    ? { backgroundColor: '#fef2f2', borderLeft: '4px solid #ef4444' }
                                    : index % 2 === 0 
                                      ? { backgroundColor: '#eff6ff', borderLeft: '4px solid #3b82f6' }
                                      : { backgroundColor: '#f0fdf4', borderLeft: '4px solid #10b981' };
                                  return (
                                    <TableRow key={key} style={rowStyle}>
                                      <TableCell className="font-medium">
                                        <span className="inline-flex items-center gap-2" style={{
                                          color: isError ? '#dc2626' : '#1d4ed8',
                                          fontWeight: '600'
                                        }}>
                                          {isError ? '❌' : '🔧'} {key.replace('_tool', '').replace('_', ' ')}
                                        </span>
                                      </TableCell>
                                      <TableCell>
                                        <div className="max-w-md break-words text-sm" style={{ color: '#374151' }}>
                                          {(() => {
                                            if (typeof value === 'object' && value?.output) {
                                              const output = value.output.trim();
                                              if (output === '[]' || output === '') {
                                                return `No results found (${key.replace('_tool', '').replace('_', ' ')})`;
                                              }
                                              return output.substring(0, 200);
                                            }
                                            return typeof value === "string"
                                              ? value.substring(0, 200)
                                              : JSON.stringify(value, null, 2).substring(0, 200);
                                          })()
                                          }
                                        </div>
                                      </TableCell>
                                      <TableCell>
                                        <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full" style={{
                                          backgroundColor: isError ? '#fecaca' : '#bbf7d0',
                                          color: isError ? '#991b1b' : '#166534',
                                          border: `1px solid ${isError ? '#f87171' : '#4ade80'}`
                                        }}>
                                          {isError ? '❌ error' : '✅ success'}
                                        </span>
                                      </TableCell>
                                    </TableRow>
                                  );
                                })}
                              </TableBody>
                            </Table>
                          </CardContent>
                        </Card>
                      )}
                      {message.content && 
                       message.content.trim() && 
                       message.content !== "Analysis complete. Check the findings panel for details." &&
                       !message.content.includes("Install nginx chart from bitnami") &&
                       !message.content.includes("Get all pods") &&
                       !message.content.includes("Add the bitnami") &&
                       message.content.length > 50 && (
                        <Card className="mt-4">
                          <CardHeader>
                            <CardTitle className="text-sm">📋 Remediation Plan</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="whitespace-pre-wrap leading-relaxed text-sm">
                              {message.content}
                            </div>
                          </CardContent>
                        </Card>
                      )}
                      <div className="mt-2 text-xs text-blue-400">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex gap-3 items-end">
                    <div className="bg-slate-700 rounded-lg rounded-tl-none p-4">
                      <div className="flex gap-2">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="mx-6 mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg">
              <div className="flex gap-2">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-red-400 text-sm">Error</div>
                  <div className="text-red-300 text-sm">{error}</div>
                </div>
              </div>
            </div>
          )}

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="border-t border-gray-300 p-6 bg-white shadow-lg">
            <div className="flex gap-3 w-full" style={{ width: '100%' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask NimbusRe Agent anything about your cluster..."
                disabled={isLoading}
                className="input-field flex-1 min-w-0"
                style={{ width: '80%', minWidth: '500px', padding: '12px 16px', fontSize: '16px' }}
              />
              <Button
                type="submit"
                disabled={isLoading || !input.trim()}
                size="lg"
                className="flex items-center gap-2 flex-shrink-0"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </Button>
            </div>

            {/* Recent Queries */}
            {recentQueries.length > 0 && messages.length > 0 && (
              <div className="mt-4 flex gap-2 flex-wrap">
                <span className="text-xs text-gray-400">Recent:</span>
                {recentQueries.map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleQuickQuery(query)}
                    disabled={isLoading}
                    className="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded text-gray-300 disabled:opacity-50"
                  >
                    {query.substring(0, 30)}...
                  </button>
                ))}
              </div>
            )}
          </form>
        </main>

        {/* Right Sidebar - Workflow Status & Findings */}
        {messages.length > 0 && (
          <aside className="w-80 border-l border-gray-300 bg-white shadow-lg overflow-y-auto p-4 space-y-4">
            {/* Status */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                {getStatusIcon(workflowState.status)}
                <h3 className="font-semibold text-white">Status</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Workflow:</span>
                  <span className="font-mono text-gray-300">
                    {workflowState.status}
                  </span>
                </div>
                {workflowState.severity && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Severity:</span>
                    <span
                      className={`badge ${getSeverityColor(
                        workflowState.severity
                      )}`}
                    >
                      {workflowState.severity}
                    </span>
                  </div>
                )}
                {workflowState.workflowType && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Type:</span>
                    <span className="font-mono text-gray-300">
                      {workflowState.workflowType}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            {(workflowState.plannedActions.length > 0 ||
              workflowState.executedActions.length > 0) && (
              <div className="card">
                <h3 className="font-semibold text-white mb-3">Actions</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {workflowState.executedActions.map((action) => (
                    <div
                      key={action.id}
                      className="text-sm p-2 bg-slate-700/50 rounded"
                    >
                      <div className="flex items-center gap-2">
                        {action.status === "succeeded" && (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        )}
                        {action.status === "failed" && (
                          <AlertCircle className="w-4 h-4 text-red-400" />
                        )}
                        {action.status === "executing" && (
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                        )}
                        <span className="font-mono text-gray-300 text-xs">
                          {action.toolName}
                        </span>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        {action.action}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Findings Summary */}
            {Object.keys(workflowState.findings).length > 0 && (
              <div className="card">
                <h3 className="font-semibold text-white mb-3">
                  Findings ({Object.keys(workflowState.findings).length})
                </h3>
                <div className="space-y-2">
                  {Object.entries(workflowState.findings).slice(0, 3).map(
                    ([key]) => (
                      <div key={key} className="text-sm text-gray-400">
                        <span className="badge badge-info">{key}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </aside>
        )}
      </div>
    </div>
  )
}

async function run_workflow(query: string, max_tools: number): Promise<SREQueryResult> {
  const response = await axios.post<SREQueryResult>(
    `/api/sre`,
    { query, max_tools },
    { timeout: 300000 }
  )

  return response.data
}

async function run_advanced_workflow(query: string, max_tools: number): Promise<SREQueryResult> {
  const response = await axios.post<SREQueryResult>(
    `/api/sre`,
    { query, max_tools },
    { timeout: 300000 }
  )

  return response.data
}

async function run_sre_session(query: string, max_tools: number): Promise<SREQueryResult> {
  const response = await axios.post<SREQueryResult>(
    `/api/sre`,
    { query, max_tools },
    { timeout: 300000 }
  )

  return response.data
}

const allowedStatuses = ["idle", "loading", "executing", "completed", "failed"] as const;
type AllowedStatus = typeof allowedStatuses[number];

function mapStatus(status: string | undefined): AllowedStatus | undefined {
  if (status && allowedStatuses.includes(status as AllowedStatus)) {
    return status as AllowedStatus;
  }
  return undefined;
}