import Button from '@mui/material/Button';
import { Tooltip } from '@mui/material';
import { ReactNode, FC } from 'react';

interface ButtonTooltipProps {
  children: ReactNode;
  onClick?: () => void;
  title?: string;
  disabled?: boolean;
  [key: string]: any;
  dataCy?: string;
}

export const ButtonTooltip: FC<ButtonTooltipProps> = ({
  children,
  onClick = () => null,
  title = 'Permission denied',
  disabled,
  dataCy,
  ...otherProps
}) => {
  return disabled ? (
    <Tooltip title={title}>
      <span>
        <Button
          disabled={disabled}
          onClick={onClick}
          data-cy={dataCy}
          {...otherProps}
        >
          {children}
        </Button>
      </span>
    </Tooltip>
  ) : (
    <Button
      disabled={disabled}
      onClick={onClick}
      data-cy={dataCy}
      {...otherProps}
    >
      {children}
    </Button>
  );
};
