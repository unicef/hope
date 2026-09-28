import { Button, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Logo } from '@components/core/Logo';
import { API_BASE_URL, LOGIN_URL } from '../../../config';
import type { FormEvent, ReactElement } from 'react';
import { useEffect, useRef, useState } from 'react';

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
const LoginError = styled(Typography)`
  && {
    color: #ffff;
    margin-top: ${({ theme }) => theme.spacing(2)};
  }
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

  const csrfInputRef = useRef<HTMLInputElement>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const clickCountRef = useRef(0);
  const clickTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const handlePageShow = (event: PageTransitionEvent) => {
      if (event.persisted) setIsSubmitting(false);
    };
    window.addEventListener('pageshow', handlePageShow);
    return () => window.removeEventListener('pageshow', handlePageShow);
  }, []);

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

  // Social login only accepts a CSRF-protected POST; the CSRF cookie is HttpOnly, so fetch the token.
  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    setIsSubmitting(true);
    setLoginError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/csrf-token`, {
        credentials: 'same-origin',
      });
      const body = response.ok ? await response.json() : null;
      const csrfToken = body?.csrf_token;
      if (typeof csrfToken !== 'string' || !csrfToken) {
        throw new Error('Missing CSRF token');
      }
      csrfInputRef.current.value = csrfToken;
      form.submit();
    } catch {
      setLoginError(t('Could not start signing in. Please try again.'));
      setIsSubmitting(false);
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
          <form method="post" action={LOGIN_URL} onSubmit={handleLogin}>
            <input
              ref={csrfInputRef}
              type="hidden"
              name="csrfmiddlewaretoken"
            />
            {next && <input type="hidden" name="next" value={next} />}
            <LoginButton
              variant="contained"
              size="large"
              type="submit"
              disabled={isSubmitting}
            >
              {t('Sign in')}
            </LoginButton>
          </form>
          {loginError && <LoginError role="alert">{loginError}</LoginError>}
        </LoginButtonContainer>
      </LoginBox>
    </Container>
  );
}
