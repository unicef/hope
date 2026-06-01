import { Button, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Logo } from '@components/core/Logo';
import { LOGIN_URL } from '../../../config';
import { ReactElement, useRef } from 'react';

const Container = styled.div`
  width: 100vw;
  height: 100vh;
  align-items: center;
  justify-content: center;
  display: flex;
`;
const LoginBox = styled.div`
  text-align: center;
  height: 538px;
  width: 533px;
  border-radius: 4px;
  background-color: ${({ theme }) => theme.hctPalette.lightBlue};
  box-shadow:
    0 0 2px 0 rgba(0, 0, 0, 0.12),
    0 2px 2px 0 rgba(0, 0, 0, 0.24);
  padding: 50px;
`;
const SubTitle = styled(Typography)`
  && {
    color: #ffff;
    font-size: 24px;
    font-weight: 300;
    line-height: 32px;
    margin-top: ${({ theme }) => theme.spacing(13)};
  }
`;
const LoginButtonContainer = styled.div`
  margin-left: ${({ theme }) => theme.spacing(11)};
  margin-right: ${({ theme }) => theme.spacing(11)};
`;
const LoginButton = styled(Button)`
  && {
    margin-top: ${({ theme }) => theme.spacing(6)};
    width: 100%;
    height: 64px;
    background-color: ${({ theme }) => theme.palette.primary.main};
    color: #ffff;
  }
`;

export function LoginPage(): ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const next = params.get('next');

  const clickCountRef = useRef(0);
  const clickTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleLogoClick = () => {
    clickCountRef.current += 1;
    if (clickTimerRef.current) clearTimeout(clickTimerRef.current);
    if (clickCountRef.current >= 4) {
      clickCountRef.current = 0;
      navigate('/surprise');
    } else {
      clickTimerRef.current = setTimeout(() => {
        clickCountRef.current = 0;
      }, 500);
    }
  };

  return (
    <Container>
      <LoginBox>
        <div
          onClick={handleLogoClick}
          style={{ cursor: 'pointer', display: 'inline-block' }}
        >
          <Logo transparent={false} displayLogoWithoutSubtitle={false} />
        </div>
        <SubTitle>{t('Login via Active Directory')}</SubTitle>
        <LoginButtonContainer>
          <LoginButton
            variant="contained"
            size="large"
            //@ts-ignore
            component="a"
            href={
              next
                ? `${LOGIN_URL}?next=${next}`
                : LOGIN_URL
            }
          >
            {t('Sign in')}
          </LoginButton>
        </LoginButtonContainer>
      </LoginBox>
    </Container>
  );
}
