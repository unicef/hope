import AssessmentIcon from '@mui/icons-material/Assessment';
import AssignmentIcon from '@mui/icons-material/Assignment';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import FeedbackIcon from '@mui/icons-material/Feedback';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import HomeIcon from '@mui/icons-material/Home';
import LinkIcon from '@mui/icons-material/Link';
import ListAltIcon from '@mui/icons-material/ListAlt';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import SendIcon from '@mui/icons-material/Send';
import SettingsIcon from '@mui/icons-material/Settings';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import { Box, Typography } from '@mui/material';
import type { FC, ReactElement } from 'react';
import styled from 'styled-components';
import { Logo } from '@components/core/Logo';
import { responsiveValue } from 'src/responsive';
import { NAVY_BLUE } from '../../../config/colors';

// Same sky blue as the login page box and the logo's baked-in background.
const LIGHT_BLUE = '#00ADEF';
const LIGHT_BLUE_TINT = '#E5F7FD';

const Container = styled(Box)`
  min-height: 100vh;
  background-color: ${LIGHT_BLUE};
  font-family: 'Roboto', sans-serif;
  box-sizing: border-box;
`;

const Content = styled(Box)`
  max-width: 960px;
  margin: 0 auto;
`;

const Card = styled(Box)`
  background-color: #ffffff;
  border-radius: 4px;
  box-shadow:
    0 0 2px 0 rgba(0, 0, 0, 0.12),
    0 2px 2px 0 rgba(0, 0, 0, 0.24);
  overflow: hidden;
`;

const SubTitle = styled(Typography)`
  && {
    color: #ffffff;
    font-weight: 300;
    text-align: center;
  }
`;

const Highlight = styled.strong`
  color: ${NAVY_BLUE};
  font-weight: 500;
`;

const Underlined = styled.a`
  color: ${NAVY_BLUE};
  text-decoration: underline;
  text-underline-offset: 3px;
`;

const Mission = styled.p`
  background-color: ${LIGHT_BLUE_TINT};
  border-left: 4px solid ${NAVY_BLUE};
  border-radius: 4px;
  padding: 16px 20px;
  margin: 24px 0 0;
  font-size: 18px;
  font-weight: 300;
  line-height: 1.6;
`;

const capabilities: { icon: ReactElement; label: string }[] = [
  { icon: <PersonAddIcon />, label: 'Collect beneficiary data' },
  { icon: <LinkIcon />, label: 'Associate data with cash programmes' },
  { icon: <GpsFixedIcon />, label: 'Create target population' },
  { icon: <ListAltIcon />, label: 'Manage payment lists' },
  {
    icon: <SendIcon />,
    label: 'Send payment lists to Financial Service Providers (FSPs)',
  },
  { icon: <CompareArrowsIcon />, label: 'Reconcile payments' },
  {
    icon: <VerifiedUserIcon />,
    label:
      'Triangulate payment verification information directly from beneficiaries',
  },
  {
    icon: <FeedbackIcon />,
    label: 'Handle grievances and feedback, as well as reporting',
  },
];

interface ComponentLink {
  name: string;
  host: string;
  onHold?: boolean;
}

interface ComponentGroup {
  title: string;
  icon: ReactElement;
  onHold?: boolean;
  items: ComponentLink[];
}

const componentGroups: ComponentGroup[] = [
  {
    title: 'HOPE',
    icon: <HomeIcon />,
    items: [
      { name: 'Hope', host: 'hope.unicef.org' },
      { name: 'Workspace', host: 'workspace.hope.unicef.org' },
      { name: 'Beneficiary', host: 'portal.hope.unicef.org', onHold: true },
    ],
  },
  {
    title: 'Data Collecting',
    icon: <AssignmentIcon />,
    items: [
      { name: 'Aurora', host: 'aurora.hope.unicef.org' },
      { name: 'Kobo', host: 'kobo.hope.unicef.org' },
    ],
  },
  {
    title: 'Services',
    icon: <SettingsIcon />,
    onHold: true,
    items: [
      { name: 'PG', host: 'payment.hope.unicef.org', onHold: true },
      { name: 'Dedup', host: 'dedup.hope.unicef.org', onHold: true },
      { name: 'Documents', host: 'documents.hope.unicef.org', onHold: true },
    ],
  },
  {
    title: 'Reporting',
    icon: <AssessmentIcon />,
    items: [
      { name: 'Report', host: 'reporting.hope.unicef.org' },
      { name: 'Dashboard', host: 'dashboard.hope.unicef.org' },
      { name: 'Cash Dashboard', host: 'cash.hope.unicef.org' },
    ],
  },
];

const OnHoldBadge: FC<{ inverted?: boolean }> = ({ inverted }) => (
  <Box
    component="span"
    sx={{
      ml: 'auto',
      px: 1.25,
      py: 0.25,
      borderRadius: '12px',
      fontSize: 12,
      fontWeight: 500,
      letterSpacing: '0.5px',
      textTransform: 'uppercase',
      whiteSpace: 'nowrap',
      color: inverted ? NAVY_BLUE : '#4E606A',
      bgcolor: inverted ? '#ffffff' : '#ECEFF1',
    }}
  >
    On hold
  </Box>
);

export const LandingPage: FC = () => (
  <Container
    sx={{
      py: responsiveValue('24px', '48px'),
      px: responsiveValue('16px', '24px'),
    }}
  >
    <Content>
      <Box
        sx={{
          textAlign: 'center',
          '& img': {
            maxWidth: '100%',
            height: responsiveValue('auto', '260px'),
          },
        }}
      >
        <Logo transparent={false} displayLogoWithoutSubtitle={false} />
      </Box>
      <SubTitle
        sx={{ fontSize: responsiveValue(20, 26), mt: 4, mb: 10, px: 2 }}
      >
        UNICEF&apos;s management information system for humanitarian cash
        transfer programmes
      </SubTitle>

      <Card sx={{ p: responsiveValue(3, 6), mb: 12 }}>
        <Typography
          variant="h4"
          component="h1"
          sx={{
            color: NAVY_BLUE,
            fontWeight: 300,
            fontSize: responsiveValue(24, 32),
            mb: 6,
          }}
        >
          The Humanitarian Cash Operations and Programme Ecosystem (HOPE)
        </Typography>
        <Typography sx={{ fontSize: 16, lineHeight: 1.7, mb: 8 }}>
          The Humanitarian Cash Operations and Programme Ecosystem (HOPE) is{' '}
          <Highlight>
            UNICEF&apos;s bespoke management information system
          </Highlight>{' '}
          for managing cash transfer programmes. It is an integrated solution
          which provides the necessary tools to manage high amounts of data
          during the implementation of Humanitarian Cash transfers in compliance
          with{' '}
          <Highlight>
            UNICEF Data Protection Policy and Information Security Standard
          </Highlight>
          .
        </Typography>

        <Typography
          variant="h6"
          component="h2"
          sx={{ color: NAVY_BLUE, fontWeight: 400, mb: 4 }}
        >
          HOPE can
        </Typography>
        <Box
          component="ul"
          sx={{
            listStyle: 'none',
            p: 0,
            m: 0,
            mb: 8,
            display: 'grid',
            gridTemplateColumns: responsiveValue('1fr', '1fr 1fr'),
            gap: 4,
          }}
        >
          {capabilities.map(({ icon, label }) => (
            <Box
              component="li"
              key={label}
              sx={{ display: 'flex', alignItems: 'center', gap: 3 }}
            >
              <Box
                sx={{
                  flexShrink: 0,
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  bgcolor: LIGHT_BLUE,
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  '& svg': { fontSize: 22 },
                }}
              >
                {icon}
              </Box>
              <Typography sx={{ fontWeight: 400 }}>{label}</Typography>
            </Box>
          ))}
        </Box>

        <Typography sx={{ fontSize: 16, lineHeight: 1.7 }}>
          HOPE is an{' '}
          <Underlined
            href="https://github.com/unicef/hope"
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontWeight: 500 }}
          >
            entirely open-source platform
          </Underlined>{' '}
          (main repository) designed to empower governments and practitioners
          with the digital tools needed to deliver cash assistance effectively.
          Whether you are a government agency, non-profit organization, or other
          entity in need of robust and adaptable digital solutions, HOPE offers
          a comprehensive suite of features that can be tailored to meet your
          specific requirements.
        </Typography>
        <Mission>
          <Highlight>Our mission</Highlight> is to facilitate the efficient and
          transparent distribution of cash assistance to those who need it most,
          ensuring that aid reaches the intended recipients in a timely and
          secure manner.
        </Mission>
      </Card>

      <SubTitle as="h2" sx={{ fontSize: responsiveValue(28, 36), mb: 8 }}>
        Components
      </SubTitle>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: responsiveValue('1fr', '1fr 1fr'),
          gap: 6,
        }}
      >
        {componentGroups.map((group) => (
          <Card key={group.title}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                px: 6,
                py: 4,
                bgcolor: NAVY_BLUE,
                color: '#ffffff',
              }}
            >
              {group.icon}
              <Typography
                component="h3"
                sx={{
                  fontSize: 15,
                  fontWeight: 500,
                  letterSpacing: '1.25px',
                  textTransform: 'uppercase',
                }}
              >
                {group.title}
              </Typography>
              {group.onHold && <OnHoldBadge inverted />}
            </Box>
            <Box component="ul" sx={{ listStyle: 'none', p: 0, m: 0 }}>
              {group.items.map((item, index) => (
                <Box
                  component="li"
                  key={item.name}
                  sx={{
                    px: 6,
                    py: 4,
                    borderTop: index === 0 ? 'none' : '1px solid #ECEFF1',
                    opacity: item.onHold ? 0.65 : 1,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography sx={{ fontWeight: 500, fontSize: 16 }}>
                      {item.name}
                    </Typography>
                    {item.onHold && !group.onHold && <OnHoldBadge />}
                  </Box>
                  <Underlined
                    href={`https://${item.host}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4,
                      wordBreak: 'break-all',
                    }}
                  >
                    {item.host}
                    <OpenInNewIcon sx={{ fontSize: 14 }} />
                  </Underlined>
                </Box>
              ))}
            </Box>
          </Card>
        ))}
      </Box>
    </Content>
  </Container>
);
