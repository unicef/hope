import { Paper } from '@mui/material';
import type { ReactElement, ReactNode } from 'react';
import styled from 'styled-components';
import { SECTION_PADDING } from 'src/responsive';

const OverviewPaper = styled(Paper)`
  margin: 20px;
`;

export function Overview({ children }: { children: ReactNode }): ReactElement {
  return (
    <OverviewPaper sx={{ padding: SECTION_PADDING }}>{children}</OverviewPaper>
  );
}
