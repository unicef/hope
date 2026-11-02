import Button from '@mui/material/Button';
import { Box, Tooltip } from '@mui/material';
import type { ReactNode, FC } from 'react';
import { responsiveValue } from 'src/responsive';

interface ButtonTooltipProps {
  children: ReactNode;
  onClick?: () => void;
  title?: string;
  disabled?: boolean;
  [key: string]: any;
  dataCy?: string;
  dataPerm?: string;
}

export const ButtonTooltip: FC<ButtonTooltipProps> = ({
  children,
  onClick = () => null,
  title = 'Permission denied',
  disabled,
  dataCy,
  dataPerm,
  ...otherProps
}) => {
  return disabled ? (
    <Tooltip title={title}>
      {/* Lets the button fill the row when header actions stack on mobile. */}
      <Box
        component="span"
        sx={{
          display: responsiveValue('inline-flex', 'inline'),
          flexDirection: 'column',
        }}
      >
        <Button
          disabled={disabled}
          onClick={onClick}
          data-cy={dataCy}
          data-perm={dataPerm}
          {...otherProps}
        >
          {children}
        </Button>
      </Box>
    </Tooltip>
  ) : (
    <Button
      disabled={disabled}
      onClick={onClick}
      data-cy={dataCy}
      data-perm={dataPerm}
      {...otherProps}
    >
      {children}
    </Button>
  );
};
