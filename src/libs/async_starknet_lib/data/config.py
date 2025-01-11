from pathlib import Path


DEFAULT_TOKEN_ABI_PATH = str(
    Path(__file__).resolve().parent / 'default_token_abi.json')


def get_base_path():
    return "m/44'/9004'/0'/0/0"


def get_class_hashes():
    return {
        'braavos_proxy': 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e,
        'braavos_implementation': 0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
        'braavos_implementation_cairo_2_5_1': 0x00816dd0297efc55dc1e7559020a3a825e81ef734b558f03c83325d4da7e6253,
        'argent_proxy': 0x025EC026985A3BF9D0CC1FE17326B245DFDC3FF89B8FDE106542A3EA56C5A918,
        'argentx_implementation': 0x33434AD846CDD5F23EB73FF09FE6FDDD568284A0FB7D1BE20EE482F044DABE2,
        'argentx_implementation_cairo_2_0_0': 0x01a736d6ed154502257f02b1ccdf4d9d1089f80811cd6acad48e6b6a9d1f2003,
        'argentx_implementation_cairo_2_4_3': 0x029927c8af6bccf3f6fda035981e765a7bdbf18a2dc0d630494f8758aa908e2b,
        'argentx_implementation_cairo_2_6_3': 0x36078334509b514626504edc9fb252328d1a240e4e948bef8d0c08dff45927f
    }
