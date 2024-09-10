import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import * as React from 'react';
import { styled } from '@mui/material/styles';

interface EnhancedTableToolbarProps {
  title: string;
}

const StyledToolbar = styled(Toolbar)(({ theme }) => ({
  paddingLeft: theme.spacing(6),
  paddingRight: theme.spacing(1),
  color: theme.palette.text.primary,
  backgroundColor: 'white',
}));

const StyledTypography = styled(Typography)({
  flex: '1 1 100%',
});

export function EnhancedTableToolbar({
  title,
}: EnhancedTableToolbarProps): React.ReactElement {
  return (
    <StyledToolbar>
      <StyledTypography data-cy="table-title" variant="h6">
        {title}
      </StyledTypography>
    </StyledToolbar>
  );
}
