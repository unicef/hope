import clsx from 'clsx';
import { DRAWER_TOP_COLOR } from '../config/colors';
import IconButton from '@material-ui/core/IconButton';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import DrawerMaterial from '@material-ui/core/Drawer';
import React from 'react';
import { makeStyles } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import DashboardIcon from '@material-ui/icons/Dashboard';
import ListItemText from '@material-ui/core/ListItemText';
import AutorenewIcon from '@material-ui/icons/Autorenew';
import PeopleIcon from '@material-ui/icons/People';
import BarChartIcon from '@material-ui/icons/BarChart';
import LayersIcon from '@material-ui/icons/Layers';
import ListSubheader from '@material-ui/core/ListSubheader';
import AssignmentIcon from '@material-ui/icons/Assignment';
import styled from 'styled-components';

const drawerWidth = 260;

export const mainListItems = (
  <div>
    <ListItem button>
      <ListItemIcon>
        <DashboardIcon />
      </ListItemIcon>
      <ListItemText primary='Country Dashboard' />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <AutorenewIcon />
      </ListItemIcon>
      <ListItemText primary='Registration Data Import' />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <PeopleIcon />
      </ListItemIcon>
      <ListItemText primary='Population' />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <BarChartIcon />
      </ListItemIcon>
      <ListItemText primary='Target Population' />
    </ListItem>
    <ListItem button>
      <ListItemIcon>
        <LayersIcon />
      </ListItemIcon>
      <ListItemText primary='Program Managment' />
    </ListItem>
  </div>
);



const useStyles = makeStyles((theme) => ({
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
}));

const ToolbarHeader = styled.div`
  display: flex;
  alignitems: center;
  justifycontent: flex-end;
  padding: 0 8px;
  color: #fff;\t
  font-family: Roboto;
  font-size: 16px;
  font-weight: 500;
  line-height: 19px;
  backgroundcolor: DRAWER_TOP_COLOR;
`;

export function Drawer({ open, handleDrawerClose }): React.ReactElement {
  const classes = useStyles({});
  return (
    <DrawerMaterial
      variant='permanent'
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
      open={open}
    >
      <ToolbarHeader
        className={classes.toolbarIcon}
        style={{ backgroundColor: DRAWER_TOP_COLOR }}
      >
        HCT-MIS PORTAL
        <IconButton
          onClick={handleDrawerClose}
          style={{ color: '#fff', opacity: 0.54 }}
        >
          <ChevronLeftIcon />
        </IconButton>
      </ToolbarHeader>
      <Divider />
      <List>{mainListItems}</List>
    </DrawerMaterial>
  );
}
