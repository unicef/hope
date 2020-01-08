import { makeStyles } from '@material-ui/core/styles';
import { theme as themeObj } from '../theme';
import React from 'react';
import { Typography } from '@material-ui/core';
import styled from 'styled-components';

import ArrowBackRounded from '@material-ui/icons/ArrowBackRounded';


const Container = styled.div`
  background-color: #fff;
  padding: 26px 44px;
  display: flex;
  justify-content: space-between;
  box-shadow: 0px 2px 4px -1px rgba(0, 0, 0, 0.2),
    0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12);
`;

interface Props {
  title: string;
  category?: string;
  children?: React.ReactElement;
}

export function PageHeader({ title, category, children }: Props) {
  return (
    <Container>
      <div>
        <div>
          {category || <Typography variant='h6'>{category}</Typography>}
          <Typography variant='h5'>{title}</Typography>
        </div>
      </div>
      <div>{children || null}</div>
    </Container>
  );
}
