#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/qcom-caf/sdm660',
    'hardware/xiaomi',
    'vendor/xiaomi/wayne',
    'vendor/xiaomi/sdm660-common',
    'vendor/qcom/opensource/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    ('vendor/bin/mlipayd@1.1'): blob_fixup()
        .remove_needed('vendor.xiaomi.hardware.mtdservice@1.0.so'),

    ('vendor/lib64/libmlipay.so | vendor/lib64/libmlipay@1.1.so'): blob_fixup()
        .remove_needed('vendor.xiaomi.hardware.mtdservice@1.0.so')
        # sed -i "s|/system/etc/firmware|/vendor/firmware\x0\x0\x0\x0|g"
        .regex_replace(br'/system/etc/firmware', br'/vendor/firmware\x00\x00\x00\x00'),

    ('vendor/lib64/vendor.xiaomi.hardware.mlipay@1.1.so | vendor/lib64/vendor.xiaomi.hardware.mlipay@1.0.so | vendor/lib64/libvendor.goodix.hardware.fingerprint@1.0.so | vendor/lib64/com.fingerprints.extension@1.0.so'): blob_fixup()
        .replace_needed('libhidlbase.so', 'libhidlbase-v32.so'),

    'vendor/lib64/libwvhidl.so': blob_fixup()
        # grep -q libcrypto_shim.so || add-needed
        .add_needed('libcrypto_shim.so', allow_existing=True)
        .clear_symbol_version('__aeabi_memcpy')
        .clear_symbol_version('__aeabi_memset')
        .clear_symbol_version('__gnu_Unwind_Find_exidx'),
}

module = ExtractUtilsModule(
    'sdm660-common',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
