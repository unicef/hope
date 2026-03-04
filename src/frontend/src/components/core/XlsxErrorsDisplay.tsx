import React from 'react';
import styled from 'styled-components';
import { Typography } from '@mui/material';

const ErrorWrapper = styled.div`
  position: sticky;
  top: 0;
  background: ${({ theme }) => theme.palette.background.paper};
  z-index: 10;
  padding: 0 20px;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const ErrorContent = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
  padding: 12px 0 20px 0;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
`;

export interface XlsxErrorsDisplayProps {
  errors: string | null;
  'data-cy'?: string;
}

export const XlsxErrorsDisplay = ({
  errors,
  ...rest
}: XlsxErrorsDisplayProps) => {
  if (!errors) return null;

  return (
    <ErrorWrapper {...rest}>
      <Typography sx={{ margin: 0, fontWeight: 600 }}>Errors:</Typography>
      <ErrorContent>{errors}</ErrorContent>
    </ErrorWrapper>
  );
};

export default XlsxErrorsDisplay;
