import styled from 'styled-components';
import { MiśTheme } from '../../../../theme';

export const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};
export const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)};
`;
export const ContentWrapper = styled.div`
  display: flex;
`;
export const SummaryBorder = styled.div`
  padding: ${({ theme }) => theme.spacing(4)};
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;
export const SummaryValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)};
`;
export const ChartContainer = styled.div`
  width: 100px;
  height: 100px;
  margin: 0 auto;
`;
