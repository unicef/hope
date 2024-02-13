import { Box, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import Divider from '@mui/material/Divider';
import DrawerMaterial from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import clsx from 'clsx';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBackendVersion } from '@hooks/useBackendVersion';
import { useFrontendVersion } from '@hooks/useFrontendVersion';
import { AlertDialog } from '../AlertDialog';
import { Logo } from '../Logo';
import { DrawerItems } from './DrawerItems';
import { resourcesItems } from './menuItems';
import { theme } from '../../../theme';

import { styled } from '@mui/system';

const ToolbarHeader = styled('div')(() => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingLeft: '51px',
  backgroundColor: matchColorToWindowOrigin(),
  color: 'white',
  borderRight: '2px solid #02367D',
  boxShadow:
    '0px 2px 4px 0px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
  ...theme.mixins.toolbar,
}));

const CollapseIcon = styled('div')({
  color: '#fff',
  opacity: 0.54,
});

const DrawerPaper = styled('div')(() => ({
  height: '100vh',
  position: 'relative',
  whiteSpace: 'nowrap',
  width: theme.drawer.width,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  borderWidth: 0,
}));

const DrawerPaperClose = styled(DrawerPaper)(() => ({
  overflowX: 'hidden',
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  width: theme.spacing(16),
  [theme.breakpoints.up('sm')]: {
    width: theme.spacing(14),
  },
}));

const Version = styled('div')({
  color: '#aaa',
  padding: 4,
  textAlign: 'center',
});

const StyledLink = styled('a')({
  color: '#233944',
  fontSize: '14px',
  fontWeight: 500,
  lineHeight: '16px',
  textDecoration: 'none',
});

const Text = styled(ListItemText)({
  '.MuiTypography-body1': {
    color: '#233944',
    fontSize: '14px',
    fontWeight: 500,
    lineHeight: '16px',
  },
});

const ResourcesText = styled('p')({
  textAlign: 'left',
  fontSize: '14px',
  color: '#aaa',
  marginLeft: '16px',
});

const ToolbarScrollBox = styled(Box)({
  overflowY: 'auto',
  height: '100%',
  borderRight: '2px solid #e1e1e1',
});

const Icon = styled(ListItemIcon)(() => ({
  minWidth: 0,
  paddingRight: theme.spacing(4),
}));

const CollapseIconButton = styled(IconButton)({
  color: '#fff',
  opacity: 0.54,
});

const matchColorToWindowOrigin = (): string => {
  const url = window.location.href;
  if (window.location.hostname === 'localhost') {
    return '#FF6600';
  }
  if (url.includes('trn')) {
    return '#BF360C';
  }
  if (url.includes('stg')) {
    return '#673AB7';
  }
  if (url.includes('dev')) {
    return '#00796B';
  }
  return '#00ADEF';
};

interface DrawerProps {
  open: boolean;
  handleDrawerClose: () => void;
  currentLocation: string;
  dataCy: string;
}

export const Drawer = ({
  open,
  handleDrawerClose,
  currentLocation,
  dataCy,
}: DrawerProps): React.ReactElement => {
  const { t } = useTranslation();
  const [showMismatchedDialog, setShowMismatchedDialog] = useState(false);
  const backendVersion = useBackendVersion();
  const frontendVersion = useFrontendVersion();
  useEffect(() => {
    if (
      !showMismatchedDialog &&
      backendVersion &&
      frontendVersion &&
      backendVersion !== frontendVersion
    ) {
      setShowMismatchedDialog(true);
    }
  }, [backendVersion, frontendVersion, showMismatchedDialog]);
  return (
    <DrawerMaterial
      variant="permanent"
      className={clsx(DrawerPaper, !open && DrawerPaperClose)}
      style={{ height: '100vh' }}
      open={open}
      data-cy={dataCy}
    >
      <ToolbarHeader>
        <Logo
          transparent={matchColorToWindowOrigin() !== '#00ADEF'}
          displayLogoWithoutSubtitle
        />
        <CollapseIconButton onClick={handleDrawerClose}>
          <ChevronLeftIcon />
        </CollapseIconButton>
      </ToolbarHeader>
      <Divider />
      <ToolbarScrollBox>
        <List>
          <DrawerItems open={open} currentLocation={currentLocation} />
        </List>
        <Box mb={2}>
          <Divider />
        </Box>
        {open && (
          <Box mb={2}>
            <ResourcesText>{t('Resources')}</ResourcesText>
          </Box>
        )}
        {resourcesItems.map((item) => (
          <ListItem button key={item.name + item.href}>
            <StyledLink
              data-cy={`nav-resources-${item.name}`}
              target="_blank"
              href={item.href}
            >
              <Box display="flex">
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
              </Box>
            </StyledLink>
          </ListItem>
        ))}
        {open && (
          <Version>
            <div>
              Backend Version:
              {backendVersion}
            </div>
            <div>
              Frontend Version:
              {frontendVersion}
            </div>
          </Version>
        )}
      </ToolbarScrollBox>
      <AlertDialog
        show={showMismatchedDialog}
        message={t('Version mismatch, please refresh page')}
      />
    </DrawerMaterial>
  );
};
