import * as React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

interface StyledLinkProps {
  fullWidth?: boolean;
  newTab?: boolean;
}

const StyledLink = styled(Link)<StyledLinkProps>`
  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')}
  overflow-wrap: break-word;
`;

const StyledLinkA = styled.a<StyledLinkProps>`
  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')}
  overflow-wrap: break-word;
`;

export const BlackLink = ({
  newTab = false,
  to = '/',
  ...props
}): React.ReactElement => {
  return newTab ? (
    <StyledLinkA
      {...props}
      href={to}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
    />
  ) : (
    <StyledLink {...props} to={to} onClick={(e) => e.stopPropagation()} />
  );
};
