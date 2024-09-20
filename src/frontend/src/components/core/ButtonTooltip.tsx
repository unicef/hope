import * as React from 'react';
import Button from '@mui/material/Button';
import { Tooltip } from '@mui/material';

interface ButtonTooltipProps {
  children: React.ReactNode;
  onClick?: () => void;
  title?: string;
  disabled?: boolean;
  [key: string]: any;
}

export const ButtonTooltip: React.FC<ButtonTooltipProps> = ({
  children,
  onClick = () => null,
  title = 'Permission denied',
  disabled,
  ...otherProps
}) => {
  return disabled ? (
    <Tooltip title={title}>
      <span>
        <Button disabled={disabled} onClick={onClick} {...otherProps}>
          {children}
        </Button>
      </span>
    </Tooltip>
  ) : (
    <Button disabled={disabled} onClick={onClick} {...otherProps}>
      {children}
    </Button>
  );
};
