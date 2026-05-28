import { GET_PEOPLE_URL } from './api/endpoints.js';

export function buildPeopleApiUrl() {
  const url = `${GET_PEOPLE_URL}${window.location.search}`;
  return url;
}