import styled from 'styled-components';

export const ButtonPlaceHolder = styled.div`
  width: 48px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;
export const Row = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  cursor: ${({ hover }) => (!hover ? 'auto' : 'pointer')};
  &:hover {
    background-color: ${({ hover }) => (!hover ? 'transparent' : '#e8e8e8')};
  }
`;
export const Cell = styled.div`
  display: flex;
  flex: ${({ weight }) => weight || 1};

  padding: 16px;
  font-size: 0.875rem;
  text-align: left;
  line-height: 1.43;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
  overflow-wrap: break-word;
  word-wrap: break-word;
  
  -ms-word-break: break-all;
  /* This is the dangerous one in WebKit, as it breaks things wherever */
  word-break: break-all;
  /* Instead use this non-standard one: */
  word-break: break-word;
  
  /* Adds a hyphen where the word breaks, if supported (No Blink) */
  -ms-hyphens: auto;
  -moz-hyphens: auto;
  -webkit-hyphens: auto;
  hyphens: auto;
`;
