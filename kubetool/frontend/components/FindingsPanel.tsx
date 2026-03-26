'use client';

import React from 'react';
import { AlertCircle, AlertTriangle, AlertOctagon, Info, CheckCircle2, TrendingDown } from 'lucide-react';

interface Finding {
  tool: string;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  message: string;
  details?: Record<string, any>;
  recommendation?: string;
}

interface FindingsPanelProps {
  findings: Record<string, any>;
  severity?: string;
  remediation_plan?: string;
}

export const FindingsPanel: React.FC<FindingsPanelProps> = ({
  findings,
  severity,
  remediation_plan,
}) => {
  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'critical':
        return <AlertOctagon className="w-5 h-5 text-red-500" />;
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case 'medium':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'low':
        return <Info className="w-5 h-5 text-blue-500" />;
      case 'info':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'critical':
        return 'border-l-4 border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'high':
        return 'border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-900/20';
      case 'medium':
        return 'border-l-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
      case 'low':
        return 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'info':
        return 'border-l-4 border-green-500 bg-green-50 dark:bg-green-900/20';
      default:
        return 'border-l-4 border-gray-500 bg-gray-50 dark:bg-gray-900/20';
    }
  };

  return (
    <div className="space-y-4">
      {/* Overall Severity */}
      {severity && (
        <div className={`p-4 rounded-lg ${getSeverityColor(severity)}`}>
          <div className="flex items-center gap-3">
            {getSeverityIcon(severity)}
            <div>
              <h3 className="font-semibold capitalize text-gray-900 dark:text-white">
                Severity: {severity}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {severity === 'critical' && 'Immediate action required'}
                {severity === 'high' && 'Action required soon'}
                {severity === 'medium' && 'Monitor and plan remediation'}
                {severity === 'low' && 'Minor issue detected'}
                {severity === 'info' && 'Informational finding'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Findings by Tool */}
      {Object.entries(findings).length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Findings
          </h4>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Tool</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Result</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {Object.entries(findings).map(([tool, data], index) => {
                  const toolFindings = Array.isArray(data) ? data : [data];
                  return toolFindings.map((finding, fIdx) => (
                    <tr key={`${index}-${fIdx}`} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-4 py-2 text-sm font-medium text-gray-900 dark:text-white">
                        {tool.replace('_tool', '').replace('_', ' ')}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 max-w-xs truncate">
                        {typeof finding === 'string'
                          ? finding.substring(0, 100)
                          : finding?.message || JSON.stringify(finding).substring(0, 100)}
                      </td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          typeof finding === 'object' && finding?.severity
                            ? finding.severity === 'critical' ? 'bg-red-100 text-red-800'
                            : finding.severity === 'high' ? 'bg-orange-100 text-orange-800'
                            : finding.severity === 'medium' ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {typeof finding === 'object' && finding?.severity ? finding.severity : 'info'}
                        </span>
                      </td>
                    </tr>
                  ));
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Remediation Plan */}
      {remediation_plan && (
        <div className="p-4 rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20">
          <div className="flex items-start gap-3">
            <TrendingDown className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
                Recommended Actions
              </h4>
              <p className="text-sm text-blue-800 dark:text-blue-300 whitespace-pre-wrap break-words">
                {remediation_plan}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {Object.entries(findings).length === 0 && !remediation_plan && (
        <div className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            No findings yet. Run a query to analyze your cluster.
          </p>
        </div>
      )}
    </div>
  );
};
