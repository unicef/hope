import { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { IconButton, Collapse } from '@mui/material';
import { ExpandLessRounded, ExpandMoreRounded } from '@mui/icons-material';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
`;
const ErrorsContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

export function ErrorsKobo({
  errors,
}: {
  errors: Record<string, any>[];
}): ReactElement {
  const [expanded, setExpanded] = useState(false);
  if (!errors || !errors.length) {
    return null;
  }
  return (
    <>
      <ErrorsContainer>
        <Error>Errors</Error>
        <IconButton
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          aria-label="show more"
        >
          {expanded ? <ExpandLessRounded /> : <ExpandMoreRounded />}
        </IconButton>
      </ErrorsContainer>
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        {errors.map((item) => (
          <Error key={item.message}>
            <strong>
              Field:
              {item.header}
            </strong>{' '}
            {item.message}
          </Error>
        ))}
      </Collapse>
    </>
  );
}
