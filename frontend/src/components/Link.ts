import styled from 'styled-components';
import { Link as OriginalLink } from 'react-router-dom';

export const Link = styled(OriginalLink)`
  text-decoration: none;

  &:focus,
  &:hover,
  &:visited,
  &:link,
  &:active {
    text-decoration: none;
  }
`;
