import * as React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

interface StyledLinkProps {
  fullWidth?: boolean;
}

export const StyledLink = styled(Link)<StyledLinkProps>`  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')}
  overflow-wrap: break-word;
`;

export function BlackLink(props): React.ReactElement {
  return <StyledLink {...props} onClick={(e) => e.stopPropagation()} />;
}
