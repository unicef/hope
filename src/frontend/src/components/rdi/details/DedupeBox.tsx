import styled from 'styled-components';
import { Box, Grid } from '@mui/material';
import { MiśTheme } from '../../../theme';
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
  options: any[];
}

export interface DedupeBoxProps {
  label: string;
  options: OptionType[];
  showBiographicalDeduplicationResult: boolean;
  showBiometricDeduplicationResult: boolean;
}

export const DedupeBox = ({
  label,
  options,
  showBiographicalDeduplicationResult,
  showBiometricDeduplicationResult,
}: DedupeBoxProps): ReactElement => {
  return (
    <GreyBox>
      <Grid container spacing={3}>
        <Grid size={12}>
          <Box display="flex" alignItems="flex-start">
            <Label data-cy={`label-${label}`} color="textSecondary">
              {label}
            </Label>
          </Box>
        </Grid>
        <Grid size={12}>
          <Grid container direction="column">
            {options.map((option) => {
              const biographicalData = option.options?.[0];
              const biometricData = option.options?.[1];

              return (
                <Grid key={option.name} container spacing={4}>
                  <Grid size={4}>
                    <BoldGrey>
                      <Small data-cy={`label-${option.name}`}>
                        {option.name}
                      </Small>
                    </BoldGrey>
                  </Grid>
                  {biographicalData && (
                    <Grid size={4} container spacing={4}>
                      <Grid size={6}>
                        <Bold data-cy={`percentage-${option.name}`}>
                          {showBiographicalDeduplicationResult
                            ? biographicalData.percentage.toFixed(2)
                            : 0}
                          %
                        </Bold>
                      </Grid>
                      <Grid size={6}>
                        <Box ml={2}>
                          <BoldGrey data-cy={`value-${option.name}`}>
                            (
                            {showBiographicalDeduplicationResult
                              ? biographicalData.count
                              : 0}
                            )
                          </BoldGrey>
                        </Box>
                      </Grid>
                    </Grid>
                  )}
                  {biometricData && (
                    <Grid size={4} container spacing={4}>
                      <Grid size={6}>
                        <Bold data-cy={`percentage-${option.name}-biometric`}>
                          {showBiometricDeduplicationResult
                            ? biometricData.percentage.toFixed(2)
                            : 0}
                          %
                        </Bold>
                      </Grid>
                      <Grid size={6}>
                        <Box ml={2}>
                          <BoldGrey data-cy={`value-${option.name}-biometric`}>
                            (
                            {showBiometricDeduplicationResult
                              ? biometricData.count
                              : 0}
                            )
                          </BoldGrey>
                        </Box>
                      </Grid>
                    </Grid>
                  )}
                </Grid>
              );
            })}
          </Grid>
        </Grid>
      </Grid>
    </GreyBox>
  );
};
