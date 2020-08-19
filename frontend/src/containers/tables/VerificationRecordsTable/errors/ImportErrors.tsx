import React, { useState } from 'react';
import styled from 'styled-components';
import { IconButton, Collapse } from '@material-ui/core';
import { ExpandLessRounded, ExpandMoreRounded } from '@material-ui/icons';
import { XlsxErrorNode } from '../../../../__generated__/graphql';

const Error = styled.div`
  color: ${({ theme }) => theme.palette.error.dark};
`;
const ErrorsContainer = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
`;

export function ImportErrors({
  errors,
}: {
  errors: XlsxErrorNode[];
}): React.ReactElement {
  const [expanded, setExpanded] = useState(false);
  if (!errors || !errors.length) {
    return null;
  }
  return (
    <>
      <ErrorsContainer data-cy='errors-container'>
        <IconButton
          onClick={() => setExpanded(!expanded)}
          aria-expanded={expanded}
          aria-label='show more'
        >
          {expanded ? <ExpandLessRounded /> : <ExpandMoreRounded />}
        </IconButton>
      </ErrorsContainer>
      <Collapse in={expanded} timeout='auto' unmountOnExit>
        {errors.map((item) => (
          <Error>
            <strong>
              {item.sheet} - {item.coordinates}
            </strong>{' '}
            {item.message}
          </Error>
        ))}
      </Collapse>
    </>
  );
}
