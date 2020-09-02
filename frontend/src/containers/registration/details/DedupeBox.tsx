import React, { useState } from 'react';
import styled from 'styled-components';
import { Grid, Box } from '@material-ui/core';
import { MiśTheme } from '../../../theme';

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
  font-size: 14px
  color: rgba(37, 59, 70, 0.6);
`;

const Small = styled.span`
  font-size: 12px;
`;
const Label = styled.span`
  ${({ theme }: { theme: MiśTheme }) => theme.styledMixins.label}
`;
export interface Props {
  label: string;
  options: {
    name: string;
    percent: number;
    value: number;
  }[];
}

export function DedupeBox({ label, options }: Props): React.ReactElement {
  return (
    <GreyBox>
      <Grid container>
        <Grid item xs={3}>
          <Box display='flex' alignItems='flex-start'>
            <Label color='textSecondary'>{label}</Label>
          </Box>
        </Grid>
        <Grid item xs={9}>
          <Grid container direction='column'>
            {options.map((option) => (
              <Grid key={option.name} container>
                <Grid item xs={4}>
                  <BoldGrey>
                    <Small>{option.name}</Small>
                  </BoldGrey>
                </Grid>
                <Grid item xs={4}>
                  <Bold>{option.percent}%</Bold>
                </Grid>
                <Grid item xs={4}>
                  <BoldGrey>{option.value}</BoldGrey>
                </Grid>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>
    </GreyBox>
  );
}
