class TestRootRoutes:

    def test_home(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "message" in resp.json()

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_info(self, client):
        resp = client.get("/info")
        data = resp.json()
        assert data["project"] == "Coding Contest Platform"
        assert data["version"] == "1.0.0"
        assert "Authentication" in data["features"]
        assert len(data["features"]) == 5
