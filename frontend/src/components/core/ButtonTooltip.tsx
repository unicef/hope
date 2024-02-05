import React from 'react';
import Button from '@material-ui/core/Button';
import { Tooltip } from '@mui/material';

export const ButtonTooltip = ({
  children,
  onClick = () => null,
  title = 'Permission denied',
  disabled,
  ...otherProps
}): React.ReactElement => {
  return disabled ? (
    <>
      <Tooltip title={title}>
        <span>
          <Button disabled={disabled} onClick={onClick} {...otherProps}>
            {children}
          </Button>
        </span>
      </Tooltip>
    </>
  ) : (
    <Button disabled={disabled} onClick={onClick} {...otherProps}>
      {children}
    </Button>
  );
};
