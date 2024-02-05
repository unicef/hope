import {
  Box,
  ListItem,
  ListItemIcon,
  ListItemText,
  makeStyles,
} from '@mui/material';
import Divider from '@mui/material/Divider';
import DrawerMaterial from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import clsx from 'clsx';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBackendVersion } from '../../../hooks/useBackendVersion';
import { useFrontendVersion } from '../../../hooks/useFrontendVersion';
import { theme as themeObj } from '../../../theme';
import { AlertDialog } from '../AlertDialog';
import { Logo } from '../Logo';
import { DrawerItems } from './DrawerItems';
import { resourcesItems } from './menuItems';

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

const useStyles = makeStyles((theme: typeof themeObj) => ({
  toolbarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingLeft: '51px',
    backgroundColor: matchColorToWindowOrigin(),
    color: 'white',
    borderRightWidth: 2,
    borderRightColor: '#02367D',
    borderRightStyle: 'solid',
    boxShadow:
      '0px 2px 4px 0px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
    ...theme.mixins.toolbar,
  },
  collapseIcon: {
    color: '#fff',
    opacity: 0.54,
  },
  drawerPaper: {
    height: '100vh',
    position: 'relative',
    whiteSpace: 'nowrap',
    width: theme.drawer.width,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    borderWidth: 0,
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(16),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(14),
    },
  },
  version: {
    color: '#aaa',
    padding: 4,
    textAlign: 'center',
  },
}));

const StyledLink = styled.a`
  color: #233944;
  font-size: 14px;
  font-weight: 500;
  line-height: 16px;
  text-decoration: none;
`;

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
  }
`;

const ResourcesText = styled('p')`
  text-align: left;
  font-size: 14px;
  color: #aaa;
  margin-left: 16px;
`;

const ToolbarScrollBox = styled(Box)`
  overflow-y: auto;
  height: 100%;
  border-right: 2px solid #e1e1e1;
`;

const Icon = styled(ListItemIcon)`
  && {
    min-width: 0;
    padding-right: ${({ theme }) => theme.spacing(4)}px;
  }
`;
interface Props {
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
}: Props): React.ReactElement => {
  const classes = useStyles({});
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
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
      style={{ height: '100vh' }}
      open={open}
      data-cy={dataCy}
    >
      <div className={classes.toolbarHeader}>
        <Logo
          transparent={matchColorToWindowOrigin() !== '#00ADEF'}
          displayLogoWithoutSubtitle
        />
        <IconButton
          onClick={handleDrawerClose}
          className={classes.collapseIcon}
        >
          <ChevronLeftIcon />
        </IconButton>
      </div>
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
          <div className={classes.version}>
            <div>Backend Version: {backendVersion}</div>
            <div>Frontend Version: {frontendVersion}</div>
          </div>
        )}
      </ToolbarScrollBox>
      <AlertDialog
        show={showMismatchedDialog}
        message={t('Version mismatch, please refresh page')}
      />
    </DrawerMaterial>
  );
};
