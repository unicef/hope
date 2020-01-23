import React from 'react';
import styled from 'styled-components';
import { LOGIN_URL } from '../../config';
import { Button, Typography } from '@material-ui/core';

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
  background-color: ${({ theme }) => theme.palette.primary.main};
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
const Separator = styled.div`
  height: 1px;
  width: 433px;
  opacity: 0.22;
  background-color: #d8d8d8;
  margin-top: ${({ theme }) => theme.spacing(8)}px;
  width: 100%;
`;
const LoginButton = styled(Button)`
  margin-top: ${({ theme }) => theme.spacing(16)}px !important;
  width: 100%;
  height: 64px;
  margin-left: ${({ theme }) => theme.spacing(11)}px;
  margin-right: ${({ theme }) => theme.spacing(11)}px;
`;

export function LoginPage(): React.ReactElement {
  return (
    <Container>
      <LoginBox>
        <Title>HCT-MIS Portal</Title>
        <SubTitle>Login via Active Directory</SubTitle>
        <Separator />
        <LoginButton
          variant='contained'
          size='large'
          component='a'
          href={LOGIN_URL}
        >
          Sign in
        </LoginButton>
      </LoginBox>
    </Container>
  );
}
