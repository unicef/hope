import { Box, Button } from '@mui/material';
import { Refresh } from '@mui/icons-material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import styled from 'styled-components';
import { responsiveValue } from 'src/responsive';
import AccessDeniedGraphic from './access_denied.png';
import HopeLogo from './access_denied_hope_logo.png';
import { useLocation } from 'react-router-dom';

const Container = styled(Box)`
  background-color: #ffffff;
  text-align: center;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
`;

const LogoContainer = styled(Box)`
  top: 20px;
  left: 20px;
`;

const SquareLogo = styled(Box)`
  display: inline-block;
  background-color: white;
  padding: 20px;
  margin-bottom: 20px;
`;

const TextContainer = styled.div`
  max-width: 450px;
  text-align: center;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: lighter;
  color: #233944;
  line-height: 32px;
`;

const Paragraph = styled.p`
  font-size: 24px;
  color: #666666;
  line-height: 32px;
`;

const SmallerPermissions = styled.p`
  font-size: 16px;
  color: #888;
  line-height: 24px;
  margin-top: 16px;
`;

export function AccessDenied() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const requiredPermissions = searchParams.get('required_permissions');
  const detail = searchParams.get('detail');
  const permissionsArray = requiredPermissions
    ? requiredPermissions.split(',')
    : [];

  const refreshAndClearCache = () => {
    window.history.back();
  };

  const handleGoBack = (): void => {
    if (window.history.length > 2) {
      window.history.go(-2);
    } else {
      window.history.back();
    }
  };

  return (
    <Container
      sx={{
        pt: responsiveValue('16px', '150px'),
        px: responsiveValue('16px', '0'),
      }}
    >
      <LogoContainer sx={{ position: responsiveValue('static', 'absolute') }}>
        <img src={HopeLogo} alt="Hope Logo" width="186" height="101" />
      </LogoContainer>
      <SquareLogo
        sx={{
          maxWidth: '100%',
          boxSizing: 'border-box',
          '& img': {
            maxWidth: '100%',
            height: responsiveValue('auto', '293px'),
          },
        }}
      >
        <img
          src={AccessDeniedGraphic}
          alt="Hand denying access"
          width="354"
          height="293"
        />
      </SquareLogo>
      <TextContainer>
        <Title data-cy="access-denied-title">Access Denied</Title>
        {detail && <Paragraph>{detail}</Paragraph>}
        {permissionsArray.length === 0 ? (
          <Paragraph>
            Sorry, the page you&apos;re trying to reach either doesn&apos;t
            exist or you don&apos;t have the required permissions to view it.
          </Paragraph>
        ) : (
          <SmallerPermissions>
            <strong>Required Permissions:</strong>
            <br />
            {permissionsArray.map((perm, idx) => (
              <span key={perm}>
                {perm}
                {idx < permissionsArray.length - 1 ? ', ' : ''}
              </span>
            ))}
          </SmallerPermissions>
        )}
      </TextContainer>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: responsiveValue(2, 0),
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            mr: responsiveValue(0, 4),
          }}
        >
          <Button
            endIcon={<Refresh />}
            variant="outlined"
            color="primary"
            onClick={refreshAndClearCache}
            data-cy="button-refresh-page"
          >
            REFRESH PAGE
          </Button>
        </Box>
        <Button
          endIcon={<ArrowBackIcon />}
          color="primary"
          variant="contained"
          onClick={handleGoBack}
          data-cy="button-go-back"
        >
          GO BACK
        </Button>
      </Box>
    </Container>
  );
}
