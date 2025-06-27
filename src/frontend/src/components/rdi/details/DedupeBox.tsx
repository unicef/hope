import styled from 'styled-components';
import { Box, Grid2 as Grid } from '@mui/material';
import { MiśTheme } from '../../../theme';
import { CountAndPercentageNode } from '@generated/graphql';
import { ReactElement } from 'react';

const GreyBox = styled.div`
  background-color: #f5f5f5;
  border: 1px solid #f5f5f5;
  border-radius: 3px;
  padding: 15px 25px;
  margin: 10px 0;
  max-width: 600px;
`;
const Bold = styled.span`
  font-weight: bold;
  font-size: 14px;
`;

const BoldGrey = styled.span`
  font-weight: bold;
  font-size: 14px;
  color: rgba(37, 59, 70, 0.6);
`;

const Small = styled.span`
  font-size: 12px;
`;
const Label = styled.span`
  ${({ theme }: { theme: MiśTheme }) => theme.styledMixins.label}
`;

export interface OptionType {
  name: string;
  options: CountAndPercentageNode[];
}

export interface DedupeBoxProps {
  label: string;
  options: OptionType[];
}

export const DedupeBox = ({ label, options }: DedupeBoxProps): ReactElement => {
  return (
    <GreyBox>
      <Grid container spacing={3}>
        <Grid size={{ xs: 12 }}>
          <Box display="flex" alignItems="flex-start">
            <Label data-cy={`label-${label}`} color="textSecondary">
              {label}
            </Label>
          </Box>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <Grid container direction="column">
            {options.map((option) => (
              <Grid key={option.name} container spacing={4}>
                <Grid size={{ xs: 4 }}>
                  <BoldGrey>
                    <Small data-cy={`label-${option.name}`}>
                      {option.name}
                    </Small>
                  </BoldGrey>
                </Grid>
                {option.options.map((item, index) => (
                  <Grid
                    key={option.name + index}
                    container
                    size={{ xs: 4 }}
                    spacing={4}
                  >
                    <Grid size={{ xs:6 }}>
                      <Bold data-cy={`percentage-${option.name}`}>
                        {item.percentage.toFixed(2)}%
                      </Bold>
                    </Grid>
                    <Grid size={{ xs:6 }}>
                      <BoldGrey data-cy={`value-${option.name}`}>
                        ({item.count})
                      </BoldGrey>
                    </Grid>
                  </Grid>
                ))}
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </GreyBox>
  );
};
