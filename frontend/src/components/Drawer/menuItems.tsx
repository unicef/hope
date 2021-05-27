import DashboardIcon from '@material-ui/icons/DashboardRounded';
import AutorenewIcon from '@material-ui/icons/AutorenewRounded';
import PeopleIcon from '@material-ui/icons/PeopleRounded';
import ListAltRounded from '@material-ui/icons/ListAltRounded';
import FlashOnRounded from '@material-ui/icons/FlashOnRounded';
import FaceIcon from '@material-ui/icons/Face';
import AttachMoney from '@material-ui/icons/AttachMoney';
import Feedback from '@material-ui/icons/Feedback';
import TrendingUpRounded from '@material-ui/icons/TrendingUpRounded';
import SupervisedUserCircle from '@material-ui/icons/SupervisedUserCircle';
import PeopleAltRoundedIcon from '@material-ui/icons/PeopleAltRounded';
import TrackChangesIcon from '@material-ui/icons/TrackChanges';
import React from 'react';
import {PERMISSIONS} from '../../config/permissions';

export const menuItems = [
  {
    name: 'Dashboard',
    href: '/#',
    selectedRegexp: /^\/$/,
    icon: <DashboardIcon />,
    permissions: [PERMISSIONS.DASHBOARD_VIEW_COUNTRY],
  },
  {
    name: 'Registration Data Import',
    href: '/registration-data-import',
    selectedRegexp: /^\/registration-data-import.*$/,
    icon: <AutorenewIcon />,
    permissions: [PERMISSIONS.RDI_VIEW_DETAILS, PERMISSIONS.RDI_VIEW_LIST],
  },
  {
    name: 'Population',
    href: '/population/household',
    selectedRegexp: /^\/population.*$/,
    icon: <PeopleIcon />,
    collapsable: true,
    permissionModule: 'POPULATION',
    secondaryActions: [
      {
        name: 'Households',
        href: '/population/household',
        selectedRegexp: /^\/population\/household.*$/,
        icon: <PeopleAltRoundedIcon />,
        permissionModule: 'HOUSEHOLDS',
      },
      {
        name: 'Individuals',
        href: '/population/individuals',
        selectedRegexp: /^\/population\/individuals.*$/,
        icon: <FaceIcon />,
        permissionModule: 'INDIVIDUALS',
      },
    ],
  },
  {
    name: 'Programme Management',
    href: '/programs',
    selectedRegexp: /^\/programs.*$/,
    icon: <FlashOnRounded />,
    permissions: [
      PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS,
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Targeting',
    href: '/target-population',
    selectedRegexp: /^\/target-population.*$/,
    icon: <ListAltRounded />,
    permissions: [
      PERMISSIONS.TARGETING_VIEW_LIST,
      PERMISSIONS.TARGETING_VIEW_DETAILS,
    ],
  },
  {
    name: 'Payment Verification',
    href: '/payment-verification',
    selectedRegexp: /^\/payment-verification.*$/,
    icon: <AttachMoney />,
    permissions: [
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Grievance and Feedback',
    href: '/grievance-and-feedback',
    selectedRegexp: /^\/grievance-and-feedback.*$/,
    icon: <Feedback />,
    permissions: [
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
      PERMISSIONS.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
    ],
  },
  {
    name: 'Reporting',
    href: '/reporting',
    selectedRegexp: /^\/reporting.*$/,
    icon: <TrendingUpRounded />,
    permissions: [PERMISSIONS.REPORTING_EXPORT],
  },
  {
    name: 'User Management',
    href: '/users-list',
    selectedRegexp: /^\/users-list.*$/,
    icon: <SupervisedUserCircle />,
    permissions: [PERMISSIONS.USER_MANAGEMENT_VIEW_LIST],
  },
  {
    name: 'Activity Log',
    href: '/activity-log',
    selectedRegexp: /^\/activity-log.*$/,
    icon: <TrackChangesIcon />,
    permissions: [PERMISSIONS.ACTIVITY_LOG_VIEW],
  },
];
