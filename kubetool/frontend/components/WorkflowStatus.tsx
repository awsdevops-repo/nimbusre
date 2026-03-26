'use client';

import React from 'react';
import { CheckCircle2, Clock, AlertCircle, Zap, DollarSign } from 'lucide-react';

interface Action {
  tool: string;
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

interface WorkflowStatusProps {
  workflow_type?: string;
  severity?: string;
  executed_actions?: Action[];
  is_loading?: boolean;
}

export const WorkflowStatus: React.FC<WorkflowStatusProps> = ({
  workflow_type = 'basic',
  severity,
  executed_actions = [],
  is_loading = false,
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Zap className="w-5 h-5 text-yellow-500 animate-pulse" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'monitoring_tool':
      case 'monitor_metrics':
        return '📊';
      case 'logs_tool':
      case 'aggregate_logs':
        return '📋';
      case 'healing_tool':
      case 'self_healing':
        return '🔧';
      case 'cost_analyzer_tool':
      case 'analyze_costs':
        return <DollarSign className="w-4 h-4" />;
      case 'ansible_tool':
      case 'ansible_inventory':
        return '🔍';
      case 'helm_tool':
      case 'helm_deploy':
        return '⚓';
      case 'kubectl_tool':
      case 'kubectl':
        return '☸️';
      default:
        return '🛠️';
    }
  };

  const getSeverityBadgeColor = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'low':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'info':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  return (
    <div className="space-y-4">
      {/* Workflow Type */}
      <div className="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Workflow Type
        </h3>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
            {workflow_type === 'advanced' ? '⚙️ Advanced' : '🚀 Basic'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {workflow_type === 'advanced'
              ? 'Approval & Rollback Enabled'
              : 'Standard Query Mode'}
          </span>
        </div>
      </div>

      {/* Severity Badge */}
      {severity && (
        <div className="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Severity Level
          </h3>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getSeverityBadgeColor(severity)}`}>
            {severity.toUpperCase()}
          </span>
        </div>
      )}

      {/* Executed Actions */}
      {executed_actions.length > 0 && (
        <div className="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Executed Actions ({executed_actions.length})
          </h3>
          <div className="space-y-2">
            {executed_actions.map((action, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 rounded bg-gray-50 dark:bg-gray-900/50"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div className="flex-shrink-0">
                    {typeof getToolIcon(action.tool) === 'string' ? (
                      <span className="text-lg">{getToolIcon(action.tool)}</span>
                    ) : (
                      getToolIcon(action.tool)
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-900 dark:text-white truncate">
                      {action.tool.replace('_tool', '')}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                      {action.action}
                    </p>
                  </div>
                </div>
                <div className="flex-shrink-0 ml-2">
                  {getStatusIcon(action.status)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {is_loading && (
        <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center gap-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-100" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce delay-200" />
            </div>
            <span className="text-sm text-blue-700 dark:text-blue-300">
              Processing query...
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
