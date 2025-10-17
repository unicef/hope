// REST API based types for Activity Log components
import type { LogEntry } from '../../../restgenerated/models/LogEntry';
import type { ChangeEvent } from 'react';

// Extended LogEntry interface with computed fields for the UI
export interface ActivityLogEntry extends LogEntry {
  id: string; // Computed unique identifier
  userDisplayName: string; // Computed from user string for display
}

// Props interface for ActivityLogTable component
export interface ActivityLogTableProps {
  logEntries: ActivityLogEntry[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: ChangeEvent<HTMLInputElement>) => void;
}

// Props interface for LogRow component
export interface LogRowProps {
  logEntry: ActivityLogEntry;
}
