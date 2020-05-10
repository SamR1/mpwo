import json
from io import BytesIO

from fittrackee_api.activities.models import Activity


def assert_activity_data_with_gpx(data):
    assert 'creation_date' in data['data']['activities'][0]
    assert (
        'Tue, 13 Mar 2018 12:44:45 GMT'
        == data['data']['activities'][0]['activity_date']
    )
    assert 'test' == data['data']['activities'][0]['user']
    assert '0:04:10' == data['data']['activities'][0]['duration']
    assert data['data']['activities'][0]['ascent'] == 0.4
    assert data['data']['activities'][0]['ave_speed'] == 4.61
    assert data['data']['activities'][0]['descent'] == 23.4
    assert data['data']['activities'][0]['distance'] == 0.32
    assert data['data']['activities'][0]['max_alt'] == 998.0
    assert data['data']['activities'][0]['max_speed'] == 5.12
    assert data['data']['activities'][0]['min_alt'] == 975.0
    assert data['data']['activities'][0]['moving'] == '0:04:10'
    assert data['data']['activities'][0]['pauses'] is None
    assert data['data']['activities'][0]['with_gpx'] is True

    records = data['data']['activities'][0]['records']
    assert len(records) == 4
    assert records[0]['sport_id'] == 2
    assert records[0]['activity_id'] == 1
    assert records[0]['record_type'] == 'MS'
    assert records[0]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[0]['value'] == 5.12
    assert records[1]['sport_id'] == 2
    assert records[1]['activity_id'] == 1
    assert records[1]['record_type'] == 'LD'
    assert records[1]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[1]['value'] == '0:04:10'
    assert records[2]['sport_id'] == 2
    assert records[2]['activity_id'] == 1
    assert records[2]['record_type'] == 'FD'
    assert records[2]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[2]['value'] == 0.32
    assert records[3]['sport_id'] == 2
    assert records[3]['activity_id'] == 1
    assert records[3]['record_type'] == 'AS'
    assert records[3]['activity_date'] == 'Tue, 13 Mar 2018 12:44:45 GMT'
    assert records[3]['value'] == 4.61


class TestEditActivityWithGpx:
    def test_it_updates_title_for_an_activity_with_gpx(
        self, app, user_1, sport_1_cycling, sport_2_running, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Activity test")),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 2 == data['data']['activities'][0]['sport_id']
        assert data['data']['activities'][0]['title'] == 'Activity test'
        assert_activity_data_with_gpx(data)

    def test_it_adds_notes_for_an_activity_with_gpx(
        self, app, user_1, sport_1_cycling, sport_2_running, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(notes="test notes")),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert data['data']['activities'][0]['title'] == 'just an activity'
        assert data['data']['activities'][0]['notes'] == 'test notes'

    def test_it_raises_403_when_editing_an_activity_from_different_user(
        self, app, user_1, user_2, sport_1_cycling, sport_2_running, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='toto@toto.com', password='87654321')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, title="Activity test")),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_it_updates_sport(
        self, app, user_1, sport_1_cycling, sport_2_running, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 2 == data['data']['activities'][0]['sport_id']
        assert data['data']['activities'][0]['title'] == 'just an activity'
        assert_activity_data_with_gpx(data)

    def test_it_returns_400_if_payload_is_empty(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'Invalid payload.' in data['message']

    def test_it_raises_500_if_sport_does_not_exists(
        self, app, user_1, sport_1_cycling, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )


class TestEditActivityWithoutGpx:
    def test_it_updates_an_activity_wo_gpx(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    activity_date='2018-05-15 15:05',
                    distance=8,
                    title='Activity test',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Tue, 15 May 2018 15:05:00 GMT'
        )
        assert data['data']['activities'][0]['user'] == 'test'
        assert data['data']['activities'][0]['sport_id'] == 2
        assert data['data']['activities'][0]['duration'] == '1:00:00'
        assert data['data']['activities'][0]['title'] == 'Activity test'
        assert data['data']['activities'][0]['ascent'] is None
        assert data['data']['activities'][0]['ave_speed'] == 8.0
        assert data['data']['activities'][0]['descent'] is None
        assert data['data']['activities'][0]['distance'] == 8.0
        assert data['data']['activities'][0]['max_alt'] is None
        assert data['data']['activities'][0]['max_speed'] == 8.0
        assert data['data']['activities'][0]['min_alt'] is None
        assert data['data']['activities'][0]['moving'] == '1:00:00'
        assert data['data']['activities'][0]['pauses'] is None
        assert data['data']['activities'][0]['with_gpx'] is False
        assert data['data']['activities'][0]['map'] is None
        assert data['data']['activities'][0]['weather_start'] is None
        assert data['data']['activities'][0]['weather_end'] is None
        assert data['data']['activities'][0]['notes'] is None

        records = data['data']['activities'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == 2
        assert records[0]['activity_id'] == 1
        assert records[0]['record_type'] == 'MS'
        assert records[0]['activity_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[0]['value'] == 8.0
        assert records[1]['sport_id'] == 2
        assert records[1]['activity_id'] == 1
        assert records[1]['record_type'] == 'LD'
        assert records[1]['activity_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == 2
        assert records[2]['activity_id'] == 1
        assert records[2]['record_type'] == 'FD'
        assert records[2]['activity_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[2]['value'] == 8.0
        assert records[3]['sport_id'] == 2
        assert records[3]['activity_id'] == 1
        assert records[3]['record_type'] == 'AS'
        assert records[3]['activity_date'] == 'Tue, 15 May 2018 15:05:00 GMT'
        assert records[3]['value'] == 8.0

    def test_it_adds_notes_to_an_activity_wo_gpx(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(notes='test notes')),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Mon, 01 Jan 2018 00:00:00 GMT'
        )
        assert data['data']['activities'][0]['user'] == 'test'
        assert data['data']['activities'][0]['sport_id'] == 1
        assert data['data']['activities'][0]['duration'] == '1:00:00'
        assert data['data']['activities'][0]['title'] is None
        assert data['data']['activities'][0]['ascent'] is None
        assert data['data']['activities'][0]['ave_speed'] == 10.0
        assert data['data']['activities'][0]['descent'] is None
        assert data['data']['activities'][0]['distance'] == 10.0
        assert data['data']['activities'][0]['max_alt'] is None
        assert data['data']['activities'][0]['max_speed'] == 10.0
        assert data['data']['activities'][0]['min_alt'] is None
        assert data['data']['activities'][0]['moving'] == '1:00:00'
        assert data['data']['activities'][0]['pauses'] is None
        assert data['data']['activities'][0]['with_gpx'] is False
        assert data['data']['activities'][0]['map'] is None
        assert data['data']['activities'][0]['weather_start'] is None
        assert data['data']['activities'][0]['weather_end'] is None
        assert data['data']['activities'][0]['notes'] == 'test notes'

        records = data['data']['activities'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == 1
        assert records[0]['activity_id'] == 1
        assert records[0]['record_type'] == 'MS'
        assert records[0]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[0]['value'] == 10.0
        assert records[1]['sport_id'] == 1
        assert records[1]['activity_id'] == 1
        assert records[1]['record_type'] == 'LD'
        assert records[1]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == 1
        assert records[2]['activity_id'] == 1
        assert records[2]['record_type'] == 'FD'
        assert records[2]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[2]['value'] == 10.0
        assert records[3]['sport_id'] == 1
        assert records[3]['activity_id'] == 1
        assert records[3]['record_type'] == 'AS'
        assert records[3]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[3]['value'] == 10.0

    def test_returns_403_when_editing_an_activity_wo_gpx_from_different_user(
        self, app, user_1, user_2, sport_1_cycling, activity_cycling_user_2
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    activity_date='2018-05-15 15:05',
                    distance=8,
                    title='Activity test',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 403
        assert 'error' in data['status']
        assert 'You do not have permissions.' in data['message']

    def test_it_updates_an_activity_wo_gpx_with_timezone(
        self,
        app,
        user_1_paris,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=2,
                    duration=3600,
                    activity_date='2018-05-15 15:05',
                    distance=8,
                    title='Activity test',
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Tue, 15 May 2018 13:05:00 GMT'
        )
        assert data['data']['activities'][0]['user'] == 'test'
        assert data['data']['activities'][0]['sport_id'] == 2
        assert data['data']['activities'][0]['duration'] == '1:00:00'
        assert data['data']['activities'][0]['title'] == 'Activity test'
        assert data['data']['activities'][0]['ascent'] is None
        assert data['data']['activities'][0]['ave_speed'] == 8.0
        assert data['data']['activities'][0]['descent'] is None
        assert data['data']['activities'][0]['distance'] == 8.0
        assert data['data']['activities'][0]['max_alt'] is None
        assert data['data']['activities'][0]['max_speed'] == 8.0
        assert data['data']['activities'][0]['min_alt'] is None
        assert data['data']['activities'][0]['moving'] == '1:00:00'
        assert data['data']['activities'][0]['pauses'] is None
        assert data['data']['activities'][0]['with_gpx'] is False

        records = data['data']['activities'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == 2
        assert records[0]['activity_id'] == 1
        assert records[0]['record_type'] == 'MS'
        assert records[0]['activity_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[0]['value'] == 8.0
        assert records[1]['sport_id'] == 2
        assert records[1]['activity_id'] == 1
        assert records[1]['record_type'] == 'LD'
        assert records[1]['activity_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == 2
        assert records[2]['activity_id'] == 1
        assert records[2]['record_type'] == 'FD'
        assert records[2]['activity_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[2]['value'] == 8.0
        assert records[3]['sport_id'] == 2
        assert records[3]['activity_id'] == 1
        assert records[3]['record_type'] == 'AS'
        assert records[3]['activity_date'] == 'Tue, 15 May 2018 13:05:00 GMT'
        assert records[3]['value'] == 8.0

    def test_it_updates_only_sport_and_distance_an_activity_wo_gpx(
        self,
        app,
        user_1,
        sport_1_cycling,
        sport_2_running,
        activity_cycling_user_1,
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(sport_id=2, distance=20)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 'creation_date' in data['data']['activities'][0]
        assert (
            data['data']['activities'][0]['activity_date']
            == 'Mon, 01 Jan 2018 00:00:00 GMT'
        )
        assert data['data']['activities'][0]['user'] == 'test'
        assert data['data']['activities'][0]['sport_id'] == 2
        assert data['data']['activities'][0]['duration'] == '1:00:00'
        assert data['data']['activities'][0]['title'] is None
        assert data['data']['activities'][0]['ascent'] is None
        assert data['data']['activities'][0]['ave_speed'] == 20.0
        assert data['data']['activities'][0]['descent'] is None
        assert data['data']['activities'][0]['distance'] == 20.0
        assert data['data']['activities'][0]['max_alt'] is None
        assert data['data']['activities'][0]['max_speed'] == 20.0
        assert data['data']['activities'][0]['min_alt'] is None
        assert data['data']['activities'][0]['moving'] == '1:00:00'
        assert data['data']['activities'][0]['pauses'] is None
        assert data['data']['activities'][0]['with_gpx'] is False

        records = data['data']['activities'][0]['records']
        assert len(records) == 4
        assert records[0]['sport_id'] == 2
        assert records[0]['activity_id'] == 1
        assert records[0]['record_type'] == 'MS'
        assert records[0]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[0]['value'] == 20.0
        assert records[1]['sport_id'] == 2
        assert records[1]['activity_id'] == 1
        assert records[1]['record_type'] == 'LD'
        assert records[1]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[1]['value'] == '1:00:00'
        assert records[2]['sport_id'] == 2
        assert records[2]['activity_id'] == 1
        assert records[2]['record_type'] == 'FD'
        assert records[2]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[2]['value'] == 20.0
        assert records[3]['sport_id'] == 2
        assert records[3]['activity_id'] == 1
        assert records[3]['record_type'] == 'AS'
        assert records[3]['activity_date'] == 'Mon, 01 Jan 2018 00:00:00 GMT'
        assert records[3]['value'] == 20.0

    def test_it_returns_400_if_payload_is_empty(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict()),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 400
        assert 'error' in data['status']
        assert 'Invalid payload.' in data['message']

    def test_it_returns_500_if_date_format_is_invalid(
        self, app, user_1, sport_1_cycling, activity_cycling_user_1
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='15/2018',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())

        assert response.status_code == 500
        assert 'error' in data['status']
        assert (
            'Error. Please try again or contact the administrator.'
            in data['message']
        )

    def test_it_returns_404_if_edited_activity_doens_not_exists(
        self, app, user_1, sport_1_cycling
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(
                dict(
                    sport_id=1,
                    duration=3600,
                    activity_date='2018-05-15 14:05',
                    distance=10,
                )
            ),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )

        data = json.loads(response.data.decode())
        assert response.status_code == 404
        assert 'not found' in data['status']
        assert len(data['data']['activities']) == 0


class TestRefreshActivityWithGpx:
    def test_refresh_an_activity_with_gpx(
        self, app, user_1, sport_1_cycling, sport_2_running, gpx_file
    ):
        client = app.test_client()
        resp_login = client.post(
            '/api/auth/login',
            data=json.dumps(dict(email='test@test.com', password='12345678')),
            content_type='application/json',
        )
        client.post(
            '/api/activities',
            data=dict(
                file=(BytesIO(str.encode(gpx_file)), 'example.gpx'),
                data='{"sport_id": 1}',
            ),
            headers=dict(
                content_type='multipart/form-data',
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token'],
            ),
        )

        # Edit some activity data
        activity = Activity.query.filter_by(id=1).first()
        activity.ascent = 1000
        activity.min_alt = -100

        response = client.patch(
            '/api/activities/1',
            content_type='application/json',
            data=json.dumps(dict(refresh=True)),
            headers=dict(
                Authorization='Bearer '
                + json.loads(resp_login.data.decode())['auth_token']
            ),
        )
        data = json.loads(response.data.decode())

        assert response.status_code == 200
        assert 'success' in data['status']
        assert len(data['data']['activities']) == 1
        assert 1 == data['data']['activities'][0]['sport_id']
        assert 0.4 == data['data']['activities'][0]['ascent']
        assert 975.0 == data['data']['activities'][0]['min_alt']
