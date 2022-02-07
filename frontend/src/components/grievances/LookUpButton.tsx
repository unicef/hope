import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';

const LookUp = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #043e91;
  border-radius: 5px;
  color: #033f91;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 500;
  cursor: pointer;
`;
const LookUpPlaceholder = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #a0b6d6;
  border-radius: 5px;
  color: #a0b6d6;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 500;
  cursor: pointer;
`;
const MarginRightSpan = styled.span`
  margin-right: 5px;
`;

export function LookUpButton({
  title,
  handleClick,
  placeholder,
}: {
  title: string;
  handleClick?: () => void;
  placeholder?: boolean;
}): React.ReactElement {
  return placeholder ? (
    <LookUpPlaceholder onClick={() => null}>
      <MarginRightSpan>
        <SearchIcon />
      </MarginRightSpan>
      <span>{title}</span>
    </LookUpPlaceholder>
  ) : (
    <LookUp onClick={handleClick}>
      <MarginRightSpan>
        <SearchIcon />
      </MarginRightSpan>
      <span>{title}</span>
    </LookUp>
  );
}
