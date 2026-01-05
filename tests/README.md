# Unit Tests

## اجرای تست‌ها

```bash
# از پوشه اصلی پروژه
python -m unittest discover tests

# یا اجرای یک فایل تست خاص
python -m unittest tests.test_main

# یا با جزئیات بیشتر
python -m unittest tests.test_main -v
```

## تست‌های موجود

- `TestValidateCryptoCode`: تست تابع اعتبارسنجی کد ارز دیجیتال
- `TestCryptocurrencyEndpoint`: تست endpoint اصلی API
- `TestAppStructure`: تست ساختار کلی اپلیکیشن

## نکته

تست‌ها از mock استفاده می‌کنند تا نیازی به API key واقعی نباشد.

