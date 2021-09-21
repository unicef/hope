import { useQuery } from '@apollo/react-hooks';
import styled from 'styled-components';
import {
  Box,
  ListItem,
  ListItemIcon,
  ListItemText,
  makeStyles,
  Typography,
} from '@material-ui/core';
import Divider from '@material-ui/core/Divider';
import DrawerMaterial from '@material-ui/core/Drawer';
import IconButton from '@material-ui/core/IconButton';
import List from '@material-ui/core/List';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import { gql } from 'apollo-boost';
import clsx from 'clsx';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import packageJson from '../../../package.json';
import { theme as themeObj } from '../../theme';
import { AlertDialog } from '../AlertDialog';
import { Logo } from '../Logo';
import { DrawerItems } from './DrawerItems';
import { resourcesItems } from './menuItems';

const matchColorToWindowOrigin = (): string => {
  const url = window.location.href;
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
  list: {
    borderRightWidth: 2,
    borderRightColor: '#E1E1E1',
    borderRightStyle: 'solid',
    height: '100%',
  },
  version: {
    borderRightWidth: 2,
    borderRightColor: '#E1E1E1',
    color: '#aaa',
    borderRightStyle: 'solid',
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

const ResourcesBox = styled(Box)`
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

const GET_BACKEND_VERSION = gql`
  {
    backendVersion @client
  }
`;

export function Drawer({
  open,
  handleDrawerClose,
  currentLocation,
  dataCy,
}: Props): React.ReactElement {
  const classes = useStyles({});
  const { t } = useTranslation();
  const [showMismatchedDialog, setShowMismatchedDialog] = useState(false);
  const { data } = useQuery(GET_BACKEND_VERSION, { fetchPolicy: 'cache-only' });
  const backendVersion = data?.backendVersion;
  const frontendVersion = packageJson.version;
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
      variant='permanent'
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
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
      <List className={classes.list}>
        <DrawerItems currentLocation={currentLocation} />
      </List>
      <ResourcesBox mb={4}>
        <Box mb={2}>
          <Divider />
        </Box>
        <Box mb={2}>
          <Typography variant='subtitle2' align='center'>
            {t('Resources')}
          </Typography>
        </Box>
        {resourcesItems.map((item) => (
          <ListItem button key={item.name + item.href}>
            <StyledLink target='_blank' href={item.href}>
              <Box display='flex'>
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
              </Box>
            </StyledLink>
          </ListItem>
        ))}
      </ResourcesBox>
      <div className={classes.version}>
        <div>Backend Version: {backendVersion}</div>
        <div>Frontend Version: {frontendVersion}</div>
      </div>
      <AlertDialog
        show={showMismatchedDialog}
        message={t('Version mismatch, please refresh page')}
      />
    </DrawerMaterial>
  );
}
