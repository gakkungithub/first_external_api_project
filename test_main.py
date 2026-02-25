# fastapiのunit testインスタンスを用いてapiのユニットテストを行う
from fastapi.testclient import TestClient
import pytest
# main.pyのfastapiインスタンス(app)を取ってきて、そのappに対してユニットテストを行う
from main import app

client = TestClient(app)

@pytest.mark.parametrize("n,expected", [
    (1,1),
    (3,2),
    (5,5),
    (10,55),
    (20,6765)
])
def test_fib_success(n, expected):
    response = client.get(f"/fib?n={n}")
    # ユニットテストによるレスポンスのステータスコードとjsonの中身が想定と合致しているかを確かめる
    assert response.status_code == 200
    assert response.json()["result"] == expected


@pytest.mark.parametrize("m", [
    8.1, 1.1, 0, -1, -10, -15
])
def test_fib_input_is_not_positive_integer(m):
    response = client.get(f"/fib?n={m}")
    data = response.json()
    if isinstance(m, int):
        assert response.status_code == 400
        assert data["status"] == "400"
        # 400 (= ValueError) に関しては下記の特定のメッセージを表示させる想定なので、それと合致するかどうか確認する
        assert data["message"] == "n must be positive integer"
    else:
        assert response.status_code == 422
        assert response.json()["status"] == "422"


# 20578以上の整数だと出力の桁数が上限の4300を超えるので入力の段階からエラーが出る想定
@pytest.mark.parametrize("l", [
    20578, 20577
])
def test_fib_input_is_positive_integer_too_big(l):
    response = client.get(f"/fib?n={l}")
    data = response.json()
    if l == 20578:
        assert response.status_code == 400
        assert data["status"] == "400"
        assert data["message"] == "n must be positive integer lower than 20578"
    else:
        assert response.status_code == 200
        assert "result" in data


def test_fib_missing_param():
    response = client.get("/fib")
    assert response.status_code == 422
    assert response.json()["status"] == "422"

def test_not_found():
    response = client.get("/unknown")
    data = response.json()
    assert response.status_code == 404
    assert data["status"] == "404"
    assert "Not Found" in data["message"]