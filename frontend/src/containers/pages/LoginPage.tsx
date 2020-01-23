import React, { useEffect } from 'react';
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from 'react-router-dom';
import styled from 'styled-components';
import { setAuthenticated } from '../../utils/utils';
import { LOGIN_URL } from '../../config';
import { Typography } from '@material-ui/core';

const Container = styled.div`
  background-color: #eee;
  width: 100vw;
  height: 100vh;
  align-items: center;
  justify-content: center;
  display: flex;
`;
const LoginBox = styled.div`
  height: 384px;
  width: 533px;
  border-radius: 4px;
  background-color: #023e90;
  box-shadow: 0 0 2px 0 rgba(0, 0, 0, 0.12), 0 2px 2px 0 rgba(0, 0, 0, 0.24);
  padding: 50px;
`;
const Title = styled(Typography)`
  color: rgba(255, 255, 255, 0.87);
  font-size: 38px !important;
  font-weight: 500;
  line-height: 32px;
`;
const SubTitle = styled(Typography)`
  color: rgba(255, 255, 255, 0.54);
  font-family: Roboto;
  font-size: 24px !important;
  font-weight: 300;
  line-height: 32px;
`;

export function LoginPage(): React.ReactElement {
  return (
    <Container>
      <LoginBox>
        <Title >HCT-MIS Portal</Title>
        <SubTitle>Login via Active Directory</SubTitle>
      </LoginBox>
    </Container>
  );
}
