import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

export const StyledLink = styled(Link)`
  color: #000;
  max-width: 150px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  display: inline-block;
`;

export function BlackLink(props): React.ReactElement {
  return <StyledLink {...props} onClick={(e) => e.stopPropagation()} />;
}
