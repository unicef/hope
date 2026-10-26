import { Button } from '@mui/material';
import type { ReactElement } from 'react';
import { useIsMobile } from 'src/responsive';

interface HeaderIconActionProps {
  /** Desktop rendering, usually a bare icon button. */
  children: ReactElement;
  icon: ReactElement;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  dataCy?: string;
  dataPerm?: string;
}

/**
 * Icon-only header action. A lone icon has no room for a hint on mobile, where header
 * actions are full-width buttons, so there it becomes a labelled outlined button.
 */
export function HeaderIconAction({
  children,
  icon,
  label,
  onClick,
  disabled,
  dataCy,
  dataPerm,
}: HeaderIconActionProps): ReactElement {
  const isMobile = useIsMobile();
  if (!isMobile) return children;
  return (
    <Button
      variant="outlined"
      color="primary"
      startIcon={icon}
      onClick={onClick}
      disabled={disabled}
      data-cy={dataCy}
      data-perm={dataPerm}
    >
      {label}
    </Button>
  );
}
