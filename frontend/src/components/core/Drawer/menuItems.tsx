import Assignment from '@mui/icons-material/Assignment';
import AttachMoney from '@mui/icons-material/AttachMoney';
import AutorenewIcon from '@mui/icons-material/AutorenewRounded';
import DashboardIcon from '@mui/icons-material/DashboardRounded';
import FaceIcon from '@mui/icons-material/Face';
import Feedback from '@mui/icons-material/Feedback';
import ListAltRounded from '@mui/icons-material/ListAltRounded';
import LocalLibrary from '@mui/icons-material/LocalLibrary';
import PeopleAltRoundedIcon from '@mui/icons-material/PeopleAltRounded';
import PaymentIcon from '@mui/icons-material/Payment';
import PeopleIcon from '@mui/icons-material/PeopleRounded';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import SupervisedUserCircle from '@mui/icons-material/SupervisedUserCircle';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import TrendingUpRounded from '@mui/icons-material/TrendingUpRounded';
import InfoIcon from '@mui/icons-material/Info';
import React from 'react';
import { PERMISSIONS } from '../../../config/permissions';

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
    href: 'https://unicef.service-now.com/cc?id=kb_search&kb_knowledge_base=be5501f9db003850d180f264f39619ee',
    icon: <LocalLibrary />,
  },
  {
    name: 'Conversations',
    href: 'https://web.yammer.com/main/groups/eyJfdHlwZSI6Ikdyb3VwIiwiaWQiOiI2NDk1MDA4In0',
    icon: <QuestionAnswerIcon />,
  },
  {
    name: 'Tools and Materials',
    href: 'https://unicef.sharepoint.com/sites/EMOPS-HOPE',
    icon: <InfoIcon />,
  },
];
