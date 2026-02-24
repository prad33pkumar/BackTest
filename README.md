# IIFL Colab Login Check

Use this script to check whether login to `https://markets.iiflcapital.com/` was successful.

## Quick run in **Google Colab**

Run these cells in order.

### 1) Install dependencies
```python
!pip -q install selenium webdriver-manager
```

### 2) Upload script to Colab
- Upload `iifl_colab_login_check.py` to your Colab session (left sidebar → Files → Upload).

### 3) Run checker (interactive credentials)
```python
!python iifl_colab_login_check.py
```

### 4) Or run with command args
```python
!python iifl_colab_login_check.py --user-id "YOUR_USER_ID" --password "YOUR_PASSWORD"
```

## Local machine run (recommended if OTP/manual interaction is required)

If your account requires OTP/2FA, local headed mode is easier:

```bash
pip install selenium webdriver-manager
python iifl_colab_login_check.py --headed
```

## Output meaning
- `✅ Login appears successful.` → redirect/UI signals suggest authenticated session.
- `❌ Login not confirmed.` + OTP/2FA message → credentials accepted but verification step pending.
- `❌ Login not confirmed.` + invalid credentials message → login failed.
