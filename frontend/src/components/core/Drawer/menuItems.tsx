import Assignment from '@material-ui/icons/Assignment';
import AttachMoney from '@material-ui/icons/AttachMoney';
import AutorenewIcon from '@material-ui/icons/AutorenewRounded';
import DashboardIcon from '@material-ui/icons/DashboardRounded';
import FaceIcon from '@material-ui/icons/Face';
import Feedback from '@material-ui/icons/Feedback';
import ListAltRounded from '@material-ui/icons/ListAltRounded';
import LocalLibrary from '@material-ui/icons/LocalLibrary';
import PeopleAltRoundedIcon from '@material-ui/icons/PeopleAltRounded';
import PaymentIcon from '@material-ui/icons/Payment';
import PeopleIcon from '@material-ui/icons/PeopleRounded';
import QuestionAnswerIcon from '@material-ui/icons/QuestionAnswer';
import SupervisedUserCircle from '@material-ui/icons/SupervisedUserCircle';
import TrackChangesIcon from '@material-ui/icons/TrackChanges';
import TrendingUpRounded from '@material-ui/icons/TrendingUpRounded';
import InfoIcon from '@material-ui/icons/Info';
import React from 'react';
import { PERMISSIONS } from '../../../config/permissions';

export const menuItems = [
  {
    name: 'Country Dashboard',
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
    icon: <Assignment />,
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
    name: 'Payment Management',
    selectedRegexp: /^\/unique.*$/,
    icon: <PaymentIcon />,
    external: true,
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
    name: 'Users',
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

export const resourcesItems = [
  {
    name: 'Knowledge Base',
    href:
      'https://unicef.service-now.com/cc?id=kb_search&kb_knowledge_base=be5501f9db003850d180f264f39619ee',
    icon: <LocalLibrary />,
  },
  {
    name: 'Conversations',
    href:
      'https://web.yammer.com/main/groups/eyJfdHlwZSI6Ikdyb3VwIiwiaWQiOiI2NDk1MDA4In0',
    icon: <QuestionAnswerIcon />,
  },
  {
    name: 'Tools and Materials',
    href: 'https://unicef.sharepoint.com/sites/EMOPS-HOPE',
    icon: <InfoIcon />,
  },
];
