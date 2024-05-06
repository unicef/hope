import styled from 'styled-components';

interface StyledBoxProps {
  disabled?: boolean;
}

export const StyledBox = styled.div<StyledBoxProps>`
  border: ${({ disabled }) => (disabled ? 0 : 1.5)}px solid #043e91;
  border-radius: 5px;
  font-size: 16px;
  padding: 16px;
  background-color: #f7faff;
`;

export const BlueText = styled.span`
  color: #033f91;
  font-weight: 500;
  font-size: 16px;
`;

export const LightGrey = styled.span`
  color: #949494;
  margin-right: 10px;
  cursor: pointer;
`;
export const DarkGrey = styled.span`
  color: #757575;
  cursor: pointer;
`;
