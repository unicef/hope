// REST API based types for Activity Log components
import type { LogEntry } from '../../../restgenerated/models/LogEntry';

// Extended LogEntry interface with computed fields for the UI
export interface ActivityLogEntry extends LogEntry {
  id: string; // Computed unique identifier
  userDisplayName: string; // Computed from user string for display
}

// Props interface for LogRow component
export interface LogRowProps {
  logEntry: ActivityLogEntry;
}
