import React from 'react';
import styled from 'styled-components';
import SearchIcon from '@material-ui/icons/Search';
import AddIcon from '@material-ui/icons/Add';

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
  addIcon,
}: {
  title: string;
  handleClick?: () => void;
  placeholder?: boolean;
  addIcon?: boolean;
}): React.ReactElement {
  return placeholder ? (
    <LookUpPlaceholder onClick={() => null}>
      <MarginRightSpan>
        {addIcon ? <AddIcon /> : <SearchIcon />}
      </MarginRightSpan>
      <span>{title}</span>
    </LookUpPlaceholder>
  ) : (
    <LookUp onClick={handleClick}>
      <MarginRightSpan>
        {addIcon ? <AddIcon /> : <SearchIcon />}
      </MarginRightSpan>
      <span>{title}</span>
    </LookUp>
  );
}
